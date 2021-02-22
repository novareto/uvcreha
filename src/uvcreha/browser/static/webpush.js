'use strict';

function urlB64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
	  .replace(/\-/g, '+')
	  .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
	outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

class WebpushService {

    button;
    text;
    worker;
    is_subscribed = false

    get pubkey() {
        const pubkey = localStorage.getItem('webpush.pubkey');
        if (!pubkey) {
            throw "No vapid public key available locally. Refresh.";
        }
        return urlB64ToUint8Array(pubkey);
    }

    get token() {
        return localStorage.getItem('webpush.token');
    }

    set token(value) {
	localStorage.setItem('webpush.token', value);
    }

    constructor(worker, subscription) {
        this.worker = worker;
	this.is_subscribed = !(subscription === null);
	if (this.is_subscribed) {
	    console.log('User IS subscribed.');
	} else {
	    console.log('User is NOT subscribed.');
	}
        this.text = document.querySelector('.js-subscription-details');
        this.button = document.querySelector('.js-push-btn');
        this.button.addEventListener('click', function() {
	    this.button.disabled = true;
	    if (this.is_subscribed) {
	        this.unsubscribe();
	    } else {
	        this.subscribe();
	    }
        }.bind(this));
        console.log("The Webpush Service is active");
    }

    static async create() {
        const worker = await navigator.serviceWorker.register(
            "/static/uvcreha/sw.js")
        console.log('Service Worker is registered', worker);
        const subscription = await worker.pushManager.getSubscription();
        const service = new WebpushService(worker, subscription)
        await service.update_serverside_subscription(subscription);
        await service.update_button();
        return service
    }

    async update_button() {
        try {
            if (Notification.permission === 'denied') {
	        this.button.textContent = 'Push Messaging Blocked.';
	        this.button.disabled = true;
	        await this.update_serverside_subscription(null);
	        return;
            }
            if (this.is_subscribed) {
	        this.button.textContent = 'Disable Push Messaging';
            } else {
	        this.button.textContent = 'Enable Push Messaging';
            }
            this.button.disabled = false;
        } catch(error) {
            console.error(error);
        }
    }

    async update_serverside_subscription(subscription) {
        const response = await fetch('/webpush/subscription', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                'subscription': subscription
            })
        });

        if (response.ok) {
                console.log("success");
        } else {
            console.log("failure", response);
        }

        if (subscription) {
	    this.text.classList.remove('is-invisible');
        } else {
	    this.text.classList.add('is-invisible');
        }
    }

    async subscribe() {
        const subscription = await this.worker.pushManager.subscribe({
	    userVisibleOnly: true,
	    applicationServerKey: this.pubkey
        })
	console.log('User is subscribed.');
	await this.update_serverside_subscription(subscription);
        this.token = JSON.stringify(subscription);
	this.is_subscribed = true;
	await this.update_button();
    }

    async unsubscribe() {
        var service = this;
        const subscription = await this.worker.pushManager.getSubscription();
        subscription.unsubscribe();
	await this.update_serverside_subscription(null);
	console.log('User is unsubscribed.');
	this.is_subscribed = false;
	await this.update_button();
    }

    async push_message(message) {

        const response = await fetch('/webpush', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                'message': message,
                'sub_token': this.token
            })
        });

        if (response.ok) {
            let json = await response.json();
            console.log("success", json);
        } else {
            console.log("failure", response);
        }
    }

}

async function initialize_webpush_service() {
    if ('serviceWorker' in navigator && 'PushManager' in window) {
        console.log('Service Worker and Push is supported');
        const pubkey = localStorage.getItem('webpush.pubkey');

        if (!pubkey) {
            let response = await fetch('/webpush/subscription');
            if (response.ok) {
                let json = await response.json();
                localStorage.setItem('webpush.pubkey', json.public_key);
            } else {
                return false;
            }
        }
        return await WebpushService.create()
    } else {
        console.warn('Push messaging is not supported');
    }
}

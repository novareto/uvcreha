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


class EventEmitter {
    constructor() {
        this.events = {};
    }
    on(event, listener) {
        if (typeof this.events[event] !== 'object') {
            this.events[event] = [];
        }
        this.events[event].push(listener);
        return () => this.removeListener(event, listener);
    }
    removeListener(event, listener) {
        if (typeof this.events[event] === 'object') {
            const idx = this.events[event].indexOf(listener);
            if (idx > -1) {
                this.events[event].splice(idx, 1);
            }
        }
    }
    emit(event, ...args) {
        if (typeof this.events[event] === 'object') {
            this.events[event].forEach(
                listener => listener.apply(this, args));
        }
    }
    once(event, listener) {
        const remove = this.on(event, (...args) => {
            remove();
            listener.apply(this, args);
        });
    }
};


class WebpushService extends EventEmitter {

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

    get denied() {
        return Notification.permission === 'denied'
    }

    constructor(worker, subscription) {
        super();
        this.worker = worker;
	this.is_subscribed = !(subscription === null);
	if (this.is_subscribed) {
	    console.log('User IS subscribed.');
	} else {
	    console.log('User is NOT subscribed.');
	}
        console.log("The Webpush Service is active");
    }

    static async create() {
        const worker = await navigator.serviceWorker.register(
            "/static/uvcreha/sw.js")
        console.log('Service Worker is registered', worker);
        const subscription = await worker.pushManager.getSubscription();
        const service = new WebpushService(worker, subscription)
        await service.update_serverside_subscription(subscription);
        return service
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
    }

    async subscribe() {
        if (this.denied) {
            await this.update_serverside_subscription(null);
            return false;
        }
        const subscription = await this.worker.pushManager.subscribe({
	    userVisibleOnly: true,
	    applicationServerKey: this.pubkey
        })
	console.log('User is subscribed.');
	await this.update_serverside_subscription(subscription);
        this.token = JSON.stringify(subscription);
	this.is_subscribed = true;
        this.emit('subscribed');
        return true;
    }

    async unsubscribe() {
        if (this.is_subscribed) {
            const subscription = await this.worker.pushManager.getSubscription();
            subscription.unsubscribe();
	    await this.update_serverside_subscription(null);
	    console.log('User is unsubscribed.');
	    this.is_subscribed = false;
	    this.emit('unsubscribed');
        }
        return true;
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
            this.emit('message pushed', message);
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

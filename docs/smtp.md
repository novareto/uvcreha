# SMTP

Mail kann man wiefolgt versenden:


```python
mailer = request.app.utilities['emailer']
with mailer.smtp() as smtp:
    mail = mailer.email("ck@novareto.de", "SUBJECT", MT)
    smtp(msg=mail.as_string(), to_addrs=('ck@novareto.de',))
```


Zum testen kann man einen example python server starten

```bash
pip3 install aiosmtpd
python3 -m aiosmtpd -n -l localhost:2525
```

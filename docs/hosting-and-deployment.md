# Hosting and Deployment

## Which Option Should I Choose?

- Use `Heroku` if you want the easiest managed option and a stable public URL. This is the default recommendation for instructors who want the least operational friction.
- Use `ngrok` if you want a free option for a small live class and are comfortable running the server on your own laptop during class. This worked fine in one `10-20 student` classroom use case, but it does come with practical limits.
- Use an `Ubuntu/Linux server` only if your department wants a stable long-term deployment and someone is comfortable managing a real server. That option is more complicated and is not covered further in this instructor packet.

## Option A: Heroku (Recommended Managed Option)

Heroku is a hosted cloud service. In plain language, that means the class connects to a website that stays online even when your laptop is closed.

Heroku costs money. Some older oTree documentation still refers to a free Heroku testing setup, so always check the current Heroku pricing page before you rely on a free or paid tier.

### Step by Step

1. Create a Heroku account at [heroku.com](https://www.heroku.com/).
2. Add a payment method in Heroku. Do this before class, not five minutes before students arrive.
3. Create an account at [oTree Hub](https://www.otreehub.com/) if you do not already have one.
4. Log in to oTree Hub and start the Heroku deployment flow for an existing oTree project.
5. When oTree Hub asks to connect to Heroku, authorize the connection.
6. Follow the oTree Hub upload or import steps for this project. This repository already includes the standard oTree deployment files such as `requirements.txt` and `Procfile`.
7. After deployment finishes, open the Heroku app settings and set `OTREE_ADMIN_PASSWORD` to a strong password.
8. Open the public app URL that Heroku gives you.
9. Log in as `admin`.
10. Create one `live_demo` session first and test it yourself before inviting students.

### How To Test Before Class

1. Open the public URL in one browser.
2. Open the same URL in a second browser or phone.
3. Confirm that both can load the site.
4. Log in to the admin page.
5. Create one demo session before you create the real class session.

### Before Class Checklist

- Heroku account created
- payment method added
- oTree Hub account created
- public app URL opens successfully
- `OTREE_ADMIN_PASSWORD` set
- one `live_demo` session tested

### Common Gotchas

- The first deployment can take a while, so do not leave it until class time.
- If an older oTree page says Heroku is free, trust the current Heroku pricing page instead.
- If the app fails on Heroku, first confirm the project works locally with `./scripts/verify_high_coverage.sh`.
- Keep the public app URL and admin password in your teaching notes before class starts.

Official references:
- [oTree server setup](https://otree.readthedocs.io/en/master/server/intro.html)
- [oTree Heroku setup](https://otree.readthedocs.io/en/master/server/heroku.html)
- [Heroku pricing](https://www.heroku.com/pricing)

## Option B: ngrok (Free Classroom Option)

ngrok creates a temporary public web address that points to the oTree server running on your own computer. In plain language, students connect to your laptop through a secure public link.

This has worked fine in one `10-20 student` live class, so it is a real option. However, the class depends on your laptop, your network connection, and the current ngrok free-plan limits.

### Step by Step

1. Create an ngrok account at [ngrok.com](https://ngrok.com/).
2. Download and install the ngrok client from the ngrok download page.
3. Log in to the ngrok dashboard and copy your auth token.
4. In a terminal, connect your computer to your ngrok account:

```bash
ngrok config add-authtoken YOUR_TOKEN_HERE
```

5. From the project root, prepare the oTree project if you have not already:

```bash
./scripts/bootstrap.sh
export OTREE_ADMIN_PASSWORD='choose-a-strong-password'
source .venv/bin/activate
```

6. Start oTree on your laptop:

```bash
otree devserver
```

7. Open a second terminal and start the ngrok tunnel to port `8000`:

```bash
ngrok http 8000
```

8. Copy the public `https://...` URL that ngrok shows you.
9. Open that public URL yourself first.
10. If it works, share that public URL with students.
11. Keep your laptop awake, plugged in, and connected to the internet for the entire class.

### How To Test Before Class

1. Start `otree devserver`.
2. Start `ngrok http 8000`.
3. Open the public ngrok URL on your phone with Wi-Fi turned off, or use a second browser that is not already logged into your local machine.
4. Confirm that the oTree page loads.
5. Create one `live_demo` session before class.

### Caveats

- Your class depends on the instructor laptop and internet connection.
- The public URL may change between sessions, depending on your ngrok plan and setup.
- The free plan has request, bandwidth, and endpoint limits, so it is better for small or moderate live classes than for always-on hosting.
- The free plan can show an ngrok browser warning/interstitial page before students reach your site.
- Test the public link yourself before class every time.

Official references:
- [ngrok getting started](https://ngrok.com/docs/getting-started/)
- [ngrok free-plan limits](https://ngrok.com/docs/pricing-limits/free-plan-limits/)
- [ngrok pricing](https://ngrok.com/pricing)

## Option C: Server (Advanced, Not Covered Here)

If your department wants a stable long-term deployment with a fixed server, use a real Ubuntu/Linux server. This is more complicated than Heroku or ngrok and is not discussed further in this instructor packet. Use the official oTree server guide if you want to go that route: [oTree Ubuntu/Linux deployment](https://otree.readthedocs.io/en/latest/server/ubuntu.html).

# Hosting And Deployment

## Which Option Should I Choose?

- Use `Heroku` if you want the easiest managed option and a stable public URL. This is the default recommendation.
- Use `ngrok` if you want a free option for a small live class and are comfortable running the server on your own laptop during class.
- Use an `Ubuntu/Linux server` only if your department wants a stable long-term deployment and someone is comfortable managing a real server. That option is more complicated and is not covered further here.

## Option A: Heroku

Heroku is a hosted cloud service. In plain language, that means students connect to a website that stays online even when your laptop is closed.

Heroku costs money. Some older oTree pages still refer to older pricing or older free tiers, so always check the current Heroku pricing page before relying on a plan.

Student note:

- some students may be eligible for Heroku credits through the GitHub Student Developer Pack
- Heroku's current student-help page describes this as platform credits spread across 12 months, with a monthly cap, so check the current terms before relying on it
- instructors should not assume they are eligible
- GitHub’s current student page says the offer is for verified students, not teachers or instructors

### Step By Step

1. Create a Heroku account.
2. Add a payment method before class day.
3. Create an `oTree Hub` account if you do not already have one.
4. Start the Heroku deployment flow from oTree Hub.
5. Authorize the Heroku connection when oTree Hub asks for it.
6. Upload or import this project in the oTree Hub flow.
7. Set `OTREE_ADMIN_PASSWORD` in the Heroku app settings.
8. Open the public app URL.
9. Log in as `admin`.
10. Create one `live_demo` session before inviting students.

### What Is `Procfile`?

`Procfile` is a small text file. Procfile tells Heroku which processes to run when the app starts. Most instructors do not need to edit it. This project already includes one.

### How To Test Before Class

1. Open the public URL in one browser.
2. Open it again on a second browser or phone.
3. Log in as `admin`.
4. Create a `live_demo` session.
5. Open the participant link on the second device.
6. Confirm that one short run works from start to finish.

### Common Gotchas

- the first deployment can take a while
- if the app fails on Heroku, first confirm the project works locally with `./scripts/verify_high_coverage.sh`
- keep the public URL and admin password in your teaching notes

Official references:

- [oTree server setup](https://otree.readthedocs.io/en/master/server/intro.html)
- [oTree Heroku setup](https://otree.readthedocs.io/en/master/server/heroku.html)
- [oTree admin page and export data](https://otree.readthedocs.io/en/latest/admin.html)
- [oTree rooms](https://otree.readthedocs.io/en/latest/rooms.html)
- [Heroku pricing](https://www.heroku.com/pricing)
- [GitHub Student Developer Pack](https://education.github.com/pack/join)
- [Heroku GitHub Students program](https://help.heroku.com/MV88YDXQ/how-do-i-sign-up-for-the-heroku-github-student-program)

## Option B: ngrok

ngrok creates a temporary public web address that points to the oTree server running on your own computer.

This has worked fine in one `10-20 student` live class, so it is a real option. The caveat is that the class depends on your laptop, your network, and the current ngrok limits.

### Step By Step

1. Create an ngrok account.
2. Download and install the ngrok client.
3. Copy your ngrok auth token from the dashboard.

Paste this into Terminal and replace `YOUR_TOKEN_HERE` with your real token:

```bash
ngrok config add-authtoken YOUR_TOKEN_HERE
```

4. Prepare the project if you have not already.

Paste this into Terminal:

```bash
./scripts/bootstrap.sh
export OTREE_ADMIN_PASSWORD='choose-a-strong-password'
source .venv/bin/activate
```

5. Start oTree on your laptop.

Paste this into Terminal:

```bash
otree devserver
```

6. Open a second terminal and start the ngrok tunnel to port `8000`.

Paste this into the second Terminal window:

```bash
ngrok http 8000
```

7. Copy the public `https://...` URL that ngrok shows you.
8. Open that public URL yourself first.
9. If it works, share it with students.
10. Keep your laptop awake, plugged in, and connected for the full class.

### How To Test Before Class

1. Start `otree devserver`.
2. Start `ngrok http 8000`.
3. Open the public ngrok URL on your phone with Wi-Fi turned off or in a second browser.
4. Create one `live_demo` session.
5. Confirm that you can get from the start page to the participant screen.

### Caveats

- the class depends on the instructor laptop and internet connection
- the public URL may change between sessions
- the free plan is better for small or moderate live classes than for always-on hosting
- some ngrok plans or free flows can show an interstitial warning page before students reach the app
- test the public link yourself before class every time

Official references:

- [ngrok getting started](https://ngrok.com/docs/getting-started/)
- [ngrok free-plan limits](https://ngrok.com/docs/pricing-limits/free-plan-limits/)
- [ngrok pricing](https://ngrok.com/pricing)

## Option C: Server

If your department wants a stable long-term deployment with a fixed server, use a real Ubuntu/Linux server. This is more complicated than `Heroku` or `ngrok` and is not discussed further in this instructor packet. Use the official oTree guide if you want that route: [oTree Ubuntu/Linux deployment](https://otree.readthedocs.io/en/latest/server/ubuntu.html).

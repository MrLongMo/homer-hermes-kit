# Homer Mover｜Grok Bot → Hermes

[中文](README.md)｜**English**

**The Ultimate Guide (with screenshots)**: https://mrlongmo.github.io/homer-hermes-kit/en/grok-bot-to-hermes/

One window that installs Hermes, adds a ready-made setup, signs you in with an AI account you already have, and moves your Grok Bot over, work files included. No terminal.

**Download (Mac, Apple silicon)**: [Homer-Mover-mac-en.zip](https://github.com/MrLongMo/homer-hermes-kit/releases/latest/download/Homer-Mover-mac-en.zip)

## How to use

1. Unzip the download. **The first time, right-click “Homer Mover” → Open → Open.**
2. Click “Install Hermes” and click through the official installer. When you see “HERMES IS READY”, **don’t click Launch Hermes yet**; close it and go back to the app.
3. Pick the AI account you have (Grok, ChatGPT, OpenRouter; none? choose the free Nous Portal plan), sign in in your browser and approve.
4. To move a Grok Bot: Start → Copy → paste into your bot → download the two files it makes → Move. You can skip this.
5. Click “Open Hermes” and **type “hi” in the chat box**. The getting-started wizard asks three questions and sets up your daily tasks.

## FAQ

- **“Can’t be opened” / “unidentified developer”**: right-click the app → Open → Open. The app isn’t signed with an Apple developer certificate yet; all the source is here.
- **Intel Mac or Windows**: official Hermes Desktop needs Apple silicon (M1 or later). Windows version coming.
- **No Grok subscription**: pick ChatGPT (Plus/Pro), OpenRouter or the free Nous Portal plan. “More options” accepts DeepSeek, Gemini, OpenAI, Claude and other API keys.
- **HTTP 403 after Grok sign-in**: a limit on some xAI plans. Paste an xAI API key under “More options” instead.
- **Not sure what to do in Hermes**: type “hi”, or tell the assistant “set me up”, “run a check-up” or “help me save tokens”.
- **Routines don’t run**: Hermes runs on your computer, so nothing runs while it’s off or asleep. Moved routines arrive paused; tell the assistant “turn on the XX routine”.
- **Stuck**: expand “Details” at the bottom of the app, take a screenshot and open an [issue](https://github.com/MrLongMo/homer-hermes-kit/issues).

## What’s inside

- `app/`: the mover (Python + pywebview). Everything goes through the official `hermes` commands; your data and API keys stay on your computer.
- `profile/homer/`: Homer’s setup (assistant, token-saving defaults, getting-started wizard, Homer Doctor, Grok Bot move and image skills).
- Tests: `python -m unittest discover -s app/tests` (uses a fake `hermes`, never touches a real install).

Not affiliated with Nous Research or xAI. Hermes is a product of Nous Research; Grok is a product of xAI. MIT licensed.

# 🤖 Create a Discord Bot for Signal Extraction

Discord has tightened security on user tokens. A bot token is more reliable and won't expire.

## Step-by-Step Bot Creation:

### **Step 1: Create Discord Application**

1. **Go to Discord Developer Portal**:
   - Visit: https://discord.com/developers/applications
   - Log in with your Discord account

2. **Create New Application**:
   - Click **"New Application"** (top right)
   - Name it: `Meta Signals Extractor` (or any name you like)
   - Click **"Create"**

### **Step 2: Create the Bot**

1. **Go to "Bot" section** (left sidebar)

2. **Click "Add Bot"**
   - Click **"Yes, do it!"** to confirm

3. **Configure Bot Settings**:
   - **Username**: Leave as is or change it
   - **Icon**: Optional, add an icon if you want
   
4. **Reset Token**:
   - Click **"Reset Token"**
   - Click **"Yes, do it!"**
   - **COPY THE TOKEN** and save it somewhere safe
   - ⚠️ **You won't see it again!** If you lose it, you'll need to reset it

5. **Enable Privileged Gateway Intents** (IMPORTANT!):
   Scroll down to "Privileged Gateway Intents" section:
   - ✅ **PRESENCE INTENT** (optional)
   - ✅ **SERVER MEMBERS INTENT** (optional)
   - ✅ **MESSAGE CONTENT INTENT** ← **CRITICAL! Must enable this!**
   
   Click **"Save Changes"** at the bottom

### **Step 3: Invite Bot to Meta Signals Server**

1. **Go to "OAuth2" → "URL Generator"** (left sidebar)

2. **Select Scopes**:
   - ✅ `bot`

3. **Select Bot Permissions**:
   - ✅ `Read Messages/View Channels`
   - ✅ `Read Message History`

4. **Copy the Generated URL** (at the bottom)

5. **Open the URL in your browser**:
   - Select **"Meta Signals"** server from the dropdown
   - Click **"Authorize"**
   - Complete the captcha
   
   ⚠️ **Note**: You need to have permission to add bots to the Meta Signals server. If you don't have this permission, you'll need to ask a server admin to add the bot for you.

### **Step 4: Update Your Config**

1. **Open** `config/config.json`

2. **Replace the token** with your new bot token:
   ```json
   "discord": {
     "token": "YOUR_NEW_BOT_TOKEN_HERE",
     ...
   }
   ```

3. **Save the file**

### **Step 5: Test the Bot**

Run the test script:
```powershell
python test_token.py
```

You should see:
```
✅ Successfully logged in as: Meta Signals Extractor
In 1 guilds:
  - Meta Signals (ID: ...)
    Channels with "alert" or "free":
      • Free Alerts
```

### **Step 6: Extract Signals**

Once the bot is working:
```powershell
python extract_signals.py
```

---

## 🆘 Troubleshooting

### "Missing Permissions" or "Forbidden"

**Problem**: Bot can't read messages

**Solution**: 
1. Go back to OAuth2 → URL Generator
2. Make sure you selected:
   - ✅ `Read Messages/View Channels`
   - ✅ `Read Message History`
3. Generate a new invite URL
4. Use it to re-invite the bot (it will update permissions)

### "Can't Add Bot to Server"

**Problem**: You're not an admin/moderator

**Options**:
1. **Ask a server admin** to add your bot (give them the invite URL)
2. **Use it on a server where you ARE admin** (for testing)
3. **Alternative**: Use the Telegram extraction method instead (if Meta Signals has a Telegram channel)

### "MESSAGE CONTENT INTENT" Error

**Problem**: Didn't enable the intent

**Solution**:
1. Go to Developer Portal → Your App → Bot
2. Scroll to "Privileged Gateway Intents"
3. Enable "MESSAGE CONTENT INTENT"
4. Save changes
5. Restart your bot

---

## 🔒 Security Notes

- **Bot tokens don't expire** (unlike user tokens)
- **Keep your bot token secret** - don't share it or commit it to GitHub
- Bot tokens are safer than user tokens for automation
- If compromised, you can reset the token in the Developer Portal

---

## 📝 Quick Checklist

Before running extraction, verify:

- [ ] Bot created in Developer Portal
- [ ] Bot token copied and saved in config.json
- [ ] MESSAGE CONTENT INTENT enabled
- [ ] Bot invited to Meta Signals server
- [ ] Bot has Read Messages + Read Message History permissions
- [ ] test_token.py shows successful login
- [ ] Bot can see "Free Alerts" channel

---

## 🎯 Next Steps

Once your bot is set up and working:

1. **Extract latest signals**: `python extract_signals.py`
2. **Run backtest**: `python full_backtest.py`
3. **Perform optimization**: `python corrected_optimization.py`
4. **Analyze results**: Check the generated reports

---

**Ready?** Create your bot now and let me know when you have the bot token!

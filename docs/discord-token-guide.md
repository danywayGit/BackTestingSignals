# How to Get Your Discord Token

## ⚠️ Important Notes

**User Token vs Bot Token:**
- **User Token**: Easier to get, works immediately, but violates Discord ToS for automation
- **Bot Token**: Official method, requires server permissions, but completely legitimate

**For personal research/backtesting**: User token is typically fine
**For production/commercial use**: Always use bot token

---

## Method 1: User Token (Quick & Easy) ⚡

### Step-by-Step Instructions:

1. **Open Discord in your web browser** (not the desktop app)
   - Go to https://discord.com/app
   - Log in to your account

2. **Open Developer Tools**
   - Press `F12` OR
   - Right-click anywhere → "Inspect Element" OR
   - `Ctrl + Shift + I` (Windows/Linux) OR
   - `Cmd + Option + I` (Mac)

3. **Go to Network Tab**
   - Click on the "Network" tab in Developer Tools
   - Make sure it's recording (red circle or "Record" button should be active)

4. **Trigger a Network Request**
   - Send a message in any channel OR
   - Refresh the page (`F5`) OR
   - Click on a different channel

5. **Find the Authorization Header**
   - Look for any request in the Network tab (usually shows many requests)
   - Click on any request to Discord's API (URLs starting with `https://discord.com/api/`)
   - Look for the "Headers" section
   - Find "Request Headers"
   - Look for `authorization: YOUR_TOKEN_HERE`

6. **Copy the Token**
   - The token will look like: `MTA1234567890.ABCDEF.1234567890ABCDEFGHIJK`
   - Copy the entire token (without any "Bearer " prefix if present)

### Alternative Method (Console):

1. **Open Console Tab** in Developer Tools
2. **Paste this code**:
   ```javascript
   (webpackChunkdiscord_app.push([[''],{},e=>{m=[];for(let c in e.c)m.push(e.c[c])}]),m).find(m=>m?.exports?.default?.getToken!==void 0).exports.default.getToken()
   ```
3. **Press Enter** - your token will be displayed

---

## Method 2: Bot Token (Official Method) 🤖

### Step-by-Step Instructions:

1. **Go to Discord Developer Portal**
   - Visit: https://discord.com/developers/applications
   - Log in with your Discord account

2. **Create New Application**
   - Click "New Application"
   - Give it a name (e.g., "Meta Signals Extractor")
   - Click "Create"

3. **Create a Bot**
   - Go to "Bot" section in the left sidebar
   - Click "Add Bot"
   - Confirm by clicking "Yes, do it!"

4. **Get Bot Token**
   - Under "Token" section, click "Copy"
   - Save this token securely

5. **Configure Bot Permissions**
   - Scroll down to "Bot Permissions"
   - Select these permissions:
     - ✅ View Channels
     - ✅ Read Message History
     - ✅ Read Messages/View Channels

6. **Invite Bot to Meta Signals Server**
   - Go to "OAuth2" → "URL Generator"
   - Select "bot" scope
   - Select the same permissions as above
   - Copy the generated URL
   - **Problem**: You need admin permissions in Meta Signals server to invite bots
   - **Solution**: Use user token method for Meta Signals

---

## Method 3: Using Browser Extensions 🔧

### Discord Token Finder Extensions:
1. Install "Discord Token Finder" extension (Chrome/Firefox)
2. Go to Discord web app
3. Click the extension icon
4. Copy your token

---

## Adding Token to Configuration 📝

Once you have your token:

1. **Open your config file**:
   ```powershell
   notepad config/config.json
   ```

2. **Replace the placeholder**:
   ```json
   {
     "discord": {
       "token": "YOUR_ACTUAL_TOKEN_HERE",
       "servers": [
         {
           "name": "Meta Signals",
           "server_id": "SERVER_ID_OPTIONAL",
           "channels": ["Free Alerts"],
           "description": "Meta Signals Free Alerts channel"
         }
       ]
     }
   }
   ```

3. **Save the file**

---

## Testing Your Token 🧪

Test if your token works:

```powershell
python -c "
import asyncio
import discord

async def test_token():
    client = discord.Client(intents=discord.Intents.default())
    try:
        await client.start('YOUR_TOKEN_HERE')
    except discord.LoginFailure:
        print('❌ Invalid token!')
    except:
        print('✅ Token is valid!')
        await client.close()

asyncio.run(test_token())
"
```

---

## Security Best Practices 🔒

1. **Never share your token** - treat it like a password
2. **Don't commit tokens to Git** - they're already in .gitignore
3. **Use environment variables** for production:
   ```powershell
   $env:DISCORD_TOKEN = "your_token_here"
   ```
4. **Regenerate tokens** if compromised

---

## Troubleshooting 🔧

### "Invalid Token" Error:
- Make sure you copied the complete token
- Check for extra spaces or characters
- Regenerate the token from Discord Developer Portal

### "403 Forbidden" Error:
- Bot doesn't have permissions
- Use user token for servers you can't add bots to

### "Can't find channels" Error:
- Make sure you're in the Meta Signals Discord server
- Check channel name spelling ("Free Alerts")
- Verify you have access to the channel

---

## For Meta Signals Specifically 🎯

**Recommended approach:**
1. Use **User Token method** (Method 1)
2. Make sure you're a member of Meta Signals Discord
3. Verify you can see the "Free Alerts" channel
4. Test with a small message limit first (like 50 messages)

**Why User Token for Meta Signals:**
- You likely don't have admin rights to add bots
- User token gives immediate access to channels you can see
- Perfect for personal research and backtesting
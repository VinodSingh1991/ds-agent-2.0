# OpenAI API Key Setup

## ⚠️ Important: API Key Required

The Disposable UI Agent requires an OpenAI API key to function. The error you're seeing:

```
"error": "OpenAI API key required. Set OPENAI_API_KEY env var or pass api_key parameter."
```

means the API key is not configured.

## 🔑 How to Get an OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click **"Create new secret key"**
4. Give it a name (e.g., "Disposable UI Agent")
5. Copy the key (starts with `sk-...`)
6. **Important:** Save it somewhere safe - you won't be able to see it again!

## ⚙️ How to Configure the API Key

### Method 1: Using .env File (Recommended)

This is the **easiest and most secure** method.

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file:**
   ```env
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```
   
   Replace `sk-your-actual-api-key-here` with your actual OpenAI API key.

3. **Restart the server:**
   ```bash
   cd api
   python start_api.py --reload
   ```

4. **Verify it works:**
   Open http://localhost:8000/docs and test the `/generate` endpoint.

### Method 2: Environment Variable (Temporary)

This sets the key for the current terminal session only.

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="sk-your-actual-api-key-here"
python start_api.py --reload
```

**Windows (CMD):**
```cmd
set OPENAI_API_KEY=sk-your-actual-api-key-here
python start_api.py --reload
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY="sk-your-actual-api-key-here"
python start_api.py --reload
```

### Method 3: System Environment Variable (Permanent)

**Windows:**
1. Search for "Environment Variables" in Start Menu
2. Click "Edit the system environment variables"
3. Click "Environment Variables" button
4. Under "User variables", click "New"
5. Variable name: `OPENAI_API_KEY`
6. Variable value: `sk-your-actual-api-key-here`
7. Click OK
8. **Restart your terminal/VS Code**

**Linux/Mac:**
Add to your `~/.bashrc` or `~/.zshrc`:
```bash
export OPENAI_API_KEY="sk-your-actual-api-key-here"
```

Then reload:
```bash
source ~/.bashrc  # or source ~/.zshrc
```

## ✅ Verify Configuration

### Check if the key is set:

**Windows (PowerShell):**
```powershell
echo $env:OPENAI_API_KEY
```

**Linux/Mac:**
```bash
echo $OPENAI_API_KEY
```

You should see your API key (or at least part of it).

### Test the API:

1. **Start the server:**
   ```bash
   cd api
   python start_api.py --reload
   ```

2. **Check health endpoint:**
   ```bash
   curl http://localhost:8000/health
   ```
   
   Should return:
   ```json
   {
     "status": "healthy",
     "agent_initialized": true,
     "version": "1.0.0"
   }
   ```

3. **Test generate endpoint:**
   Open http://localhost:8000/docs and try the `/generate` endpoint with:
   ```json
   {
     "query": "show me all leads",
     "data": [
       {"id": 1, "name": "Acme Corp", "revenue": 75000}
     ]
   }
   ```

## 🐛 Debugging in VS Code

If you're using VS Code debug mode:

1. **Create/edit `.env` file** in the project root
2. **Add your API key:**
   ```env
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```
3. **Press F5** to start debugging
4. The `.env` file will be automatically loaded

The debug configuration in `.vscode/launch.json` is already set up to load the `.env` file.

## 🔒 Security Best Practices

### ✅ DO:
- Store API key in `.env` file
- Add `.env` to `.gitignore` (already done)
- Use environment variables
- Rotate keys periodically
- Use separate keys for dev/prod

### ❌ DON'T:
- Commit `.env` file to Git
- Share your API key publicly
- Hardcode API key in source code
- Use the same key across multiple projects

## 💰 API Costs

The Disposable UI Agent uses OpenAI's GPT-4 model. Typical costs:

- **Query analysis:** ~$0.001 per request
- **Layout generation:** ~$0.01-0.05 per request
- **Total:** ~$0.01-0.06 per layout generation

Set up billing limits in your OpenAI account to avoid unexpected charges.

## 🆘 Troubleshooting

### "Invalid API key"
- Check that you copied the entire key (starts with `sk-`)
- Verify the key is active in your OpenAI dashboard
- Try creating a new key

### "API key not found"
- Verify `.env` file is in the project root (not in `api/` folder)
- Check the file is named exactly `.env` (not `.env.txt`)
- Restart the server after setting the key
- In VS Code, restart the debug session

### "Insufficient quota"
- Check your OpenAI account has credits
- Add payment method at https://platform.openai.com/account/billing

### Still not working?
1. Check the server logs: `api/logs/api.log`
2. Verify the `.env` file location and content
3. Try setting the environment variable directly in terminal
4. Restart VS Code/terminal completely

## 📚 Additional Resources

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [OpenAI API Keys](https://platform.openai.com/api-keys)
- [OpenAI Pricing](https://openai.com/pricing)
- [Setup Guide](SETUP_GUIDE.md)

---

**Need help?** Check the [SETUP_GUIDE.md](SETUP_GUIDE.md) for complete setup instructions.


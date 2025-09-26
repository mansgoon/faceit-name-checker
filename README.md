# FACEIT Name Availability Checker

A Python script that checks thousands of FACEIT usernames for availability using real English words and comprehensive tracking.

## 🚀 Features

- **Smart Word Generation**: Uses Random Word API for real 3-4 letter English words
- **Persistent Tracking**: Automatically saves progress and resumes where you left off
- **Rate Limiting**: Built-in delays to avoid getting blocked
- **Comprehensive Reporting**: Detailed statistics and organized results
- **Error Handling**: Robust retry logic and debugging

## 📁 Files Created

The script automatically creates and manages these files:

### `checked_names.txt`
- Contains all names that have been checked (one per line)
- Prevents duplicate checks when restarting the script
- Automatically loaded on startup

### `available_names.txt` 
- Contains all available names found with timestamps
- Format: `username (idle user) - Found: 2025-01-22 15:30:45`
- Automatically updated as names are found

### `faceit_summary_YYYY-MM-DD_HH-MM-SS.txt`
- Generated at the end of each session
- Complete statistics and organized results
- Separates fully available vs idle user names

## 🛠️ Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get your FACEIT cookies:**
   - Login to FACEIT in your browser
   - Go to https://www.faceit.com/en/shop
   - Press F12 → Application → Cookies → www.faceit.com
   - Find these cookie values:
     - `__Host-AuthSession`
     - `__Host-FaceitGatewayAuthorization`
     - `cf_clearance`

3. **Run the script:**
   ```bash
   python check.py
   ```

## 🎯 Usage

### First Run
- Script will ask for your authentication cookies
- Choose option 1 for random English words (recommended)
- Progress is automatically saved

### Subsequent Runs
- Script loads previous progress automatically
- Skips already checked names
- Continues building your available names list

### Example Output
```
📋 Loaded 1,247 previously checked names
✅ Loaded 23 previously found available names
🎯 3,891 new names to check

[  1/3891] Checking: cat... ❌ TAKEN
[  2/3891] Checking: dog... ✅ AVAILABLE
[  3/3891] Checking: fire... ❌ TAKEN
...
```

### Custom Length Example
```
🎯 Custom Length Word Generator
Examples: 5 (for 5-letter words), 5,6,7 (for multiple lengths)
Enter word lengths (comma-separated): 5,6
Words per length (default 1000): 1500

📝 Fetching 1500 words each for lengths: [5, 6]
Fetching 1500 random 5-letter words from API...
Retrieved 1489 unique 5-letter words
Fetching 1500 random 6-letter words from API...
Retrieved 1495 unique 6-letter words
✅ Generated 2984 words
⏱️  Estimated time: 0.4 hours
Continue with availability check? (y/n): y
```

## 📊 Options

1. **Random English words (3-4 letters)** - Recommended
   - Fetches 4,000 real dictionary words
   - Higher chance of desirable names
   - Most efficient approach

2. **Custom length words (5, 6, 7+ letters)**
   - Choose any word length(s) from 1-20 characters
   - Fetches real dictionary words from Random Word API
   - Perfect for longer, more unique usernames
   - Examples: 5-letter words, 6-letter words, or mix multiple lengths

3. **ALL 3-letter combinations (17,576 names)**
   - Every possible aaa-zzz combination
   - Takes ~2.5 hours to complete
   - Comprehensive but includes nonsense combinations

4. **ALL 4-letter combinations (456,976 names)**
   - Every possible aaaa-zzzz combination  
   - Takes 60+ hours to complete
   - Extremely comprehensive

5. **Custom list**
   - Enter specific names to check
   - Useful for testing specific words

## 📈 Statistics

The script tracks:
- Total names checked across all sessions
- Available names found (fully available vs idle users)
- Success rates and progress
- Timestamps for all discoveries

## 🔧 Troubleshooting

### "Still getting 403 errors"
- Your cookies may have expired
- Get fresh cookies from your browser
- Make sure you're logged into FACEIT

### "Connection failed"
- Check your internet connection
- Try disabling VPN if using one
- Verify FACEIT isn't blocking your IP

### "No new names to check"
- All names in the current list have been checked
- Try a different option (e.g., switch from option 1 to option 2)
- Delete `checked_names.txt` to start fresh (you'll lose progress)

## 💡 Tips

- **Run overnight**: Let the script run for hours to check thousands of names
- **Multiple sessions**: Stop and restart anytime - progress is saved
- **Check idle users**: Names marked "idle user" may become available later
- **Monitor rate limits**: Script will slow down automatically if rate limited
- **Try longer words**: 5-6 letter words often have higher availability rates
- **Mix lengths**: Use "5,6,7" to check multiple word lengths in one session
- **Premium names**: Longer words (7+) are often completely unclaimed

## ⚠️ Important Notes

- Requires valid FACEIT login cookies
- Respects rate limits (1-second delays)
- Available names may be claimed by others quickly
- Idle user names might become available if the user is inactive

## 🤝 Contributing

Feel free to submit issues or improvements to make the script even better! 
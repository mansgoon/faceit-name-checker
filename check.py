import requests
import time
import json
import string
import itertools
from datetime import datetime
import sys

class FaceitNameChecker:
    def __init__(self, cookies=None):
        self.base_url = "https://www.faceit.com/api/shop/v2/nickname-availability/"
        self.available_names = []
        self.checked_count = 0
        self.total_count = 0
        self.session = requests.Session()
        
        # File paths for persistence
        self.checked_names_file = "checked_names.txt"
        self.available_names_file = "available_names.txt"
        
        # Load existing data
        self.checked_names_set = self.load_checked_names()
        self.load_available_names()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Ch-Ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Referer': 'https://www.faceit.com/en/shop',
            'Priority': 'u=1, i'
        })
        
        # Add cookies if provided
        if cookies:
            self.session.headers['Cookie'] = cookies
            print("✅ Using provided authentication cookies")
    
    def check_name_availability(self, name, max_retries=3):
        """Check if a name is available on FACEIT with retry logic"""
        for attempt in range(max_retries):
            try:
                url = f"{self.base_url}{name}"
                response = self.session.get(url, timeout=15)
                
                if response.status_code == 200:
                    try:
                        # Debug response details
                        content_encoding = response.headers.get('content-encoding', 'none')
                        content_type = response.headers.get('content-type', 'unknown')
                        
                        # Check if response is properly decompressed
                        if len(response.content) != len(response.text.encode('utf-8')):
                            print(f"\n🔍 Compression issue detected for {name}")
                            print(f"    Content-Encoding: {content_encoding}")
                            print(f"    Raw content length: {len(response.content)}")
                            print(f"    Text length: {len(response.text)}")
                        
                        data = response.json()
                        payload = data.get('payload', {})
                        is_available = payload.get('available', False)
                        belongs_to_idle = payload.get('belongs_to_idle_user', False)
                        
                        return {
                            'name': name,
                            'available': is_available,
                            'belongs_to_idle_user': belongs_to_idle,
                            'status': 'success'
                        }
                    except (json.JSONDecodeError, ValueError) as e:
                        print(f"\n🔍 Got HTTP 200 but invalid JSON for {name}")
                        print(f"    JSON Error: {e}")
                        print(f"    Content-Type: {response.headers.get('content-type', 'unknown')}")
                        print(f"    Content-Encoding: {response.headers.get('content-encoding', 'none')}")
                        print(f"    Response length: {len(response.content)} bytes")
                        print(f"    First 100 bytes (hex): {response.content[:100].hex()}")
                        
                        # Try to decode manually if it's compressed
                        try:
                            import gzip
                            import zlib
                            
                            if response.headers.get('content-encoding') == 'gzip':
                                decompressed = gzip.decompress(response.content)
                                data = json.loads(decompressed.decode('utf-8'))
                                payload = data.get('payload', {})
                                is_available = payload.get('available', False)
                                belongs_to_idle = payload.get('belongs_to_idle_user', False)
                                
                                print(f"    ✅ Manual gzip decompression successful!")
                                return {
                                    'name': name,
                                    'available': is_available,
                                    'belongs_to_idle_user': belongs_to_idle,
                                    'status': 'success'
                                }
                        except Exception as decomp_error:
                            print(f"    Manual decompression failed: {decomp_error}")
                        
                        return {
                            'name': name,
                            'available': False,
                            'belongs_to_idle_user': False,
                            'status': 'error_invalid_json'
                        }
                elif response.status_code == 403:
                    if attempt < max_retries - 1:
                        # Wait longer on 403 and retry
                        time.sleep(2 * (attempt + 1))
                        continue
                    else:
                        return {
                            'name': name,
                            'available': False,
                            'belongs_to_idle_user': False,
                            'status': 'error_403_blocked'
                        }
                elif response.status_code == 429:  # Rate limited
                    if attempt < max_retries - 1:
                        time.sleep(5 * (attempt + 1))
                        continue
                    else:
                        return {
                            'name': name,
                            'available': False,
                            'belongs_to_idle_user': False,
                            'status': 'error_429_rate_limit'
                        }
                else:
                    print(f"\n🔍 HTTP {response.status_code} for {name}: {response.text[:200]}")
                    return {
                        'name': name,
                        'available': False,
                        'belongs_to_idle_user': False,
                        'status': f'error_{response.status_code}'
                    }
                    
            except requests.exceptions.JSONDecodeError as e:
                print(f"\n🔍 JSON decode error for {name}: {e}")
                try:
                    print(f"    Raw response: {response.text[:300]}")
                    print(f"    Status code: {response.status_code}")
                    print(f"    Headers: {dict(response.headers)}")
                except:
                    print("    Could not access response details")
                if attempt < max_retries - 1:
                    print(f"   Retrying in {1 * (attempt + 1)} seconds...")
                    time.sleep(1 * (attempt + 1))
                    continue
                else:
                    return {
                        'name': name,
                        'available': False,
                        'belongs_to_idle_user': False,
                        'status': 'error_json_decode'
                    }
            except requests.exceptions.RequestException as e:
                print(f"\n🔍 Request error for {name}: {type(e).__name__}: {e}")
                if attempt < max_retries - 1:
                    print(f"   Retrying in {1 * (attempt + 1)} seconds...")
                    time.sleep(1 * (attempt + 1))
                    continue
                else:
                    return {
                        'name': name,
                        'available': False,
                        'belongs_to_idle_user': False,
                        'status': f'error_request_{type(e).__name__}'
                    }
    
    def generate_3_letter_combinations(self):
        """Generate all possible 3-letter combinations"""
        letters = string.ascii_lowercase
        combinations = []
        
        # Generate all possible 3-letter combinations
        for combo in itertools.product(letters, repeat=3):
            combinations.append(''.join(combo))
        
        return combinations
    
    def generate_4_letter_combinations(self):
        """Generate all possible 4-letter combinations"""
        letters = string.ascii_lowercase
        combinations = []
        
        # Generate all possible 4-letter combinations
        for combo in itertools.product(letters, repeat=4):
            combinations.append(''.join(combo))
        
        return combinations
    
    def fetch_random_words(self, length, count=1000):
        """Fetch random words of specific length from Random Word API"""
        url = f"https://random-word-api.herokuapp.com/word?length={length}&number={count}"
        
        try:
            print(f"Fetching {count} random {length}-letter words from API...")
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                words = response.json()
                # Convert to lowercase and remove duplicates
                unique_words = list(set([word.lower() for word in words if isinstance(word, str)]))
                print(f"Retrieved {len(unique_words)} unique {length}-letter words")
                return unique_words
            else:
                print(f"Error fetching words: HTTP {response.status_code}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching random words: {e}")
            return []
    
    def generate_random_word_combinations(self):
        """Generate combinations using Random Word API for 3 and 4 letter words"""
        all_words = []
        
        # Fetch 3-letter words
        words_3 = self.fetch_random_words(3, 2000)
        all_words.extend(words_3)
        
        # Fetch 4-letter words  
        words_4 = self.fetch_random_words(4, 2000)
        all_words.extend(words_4)
        
        return all_words
    
    def generate_custom_length_words(self, lengths, count_per_length=1000):
        """Generate words using Random Word API for custom lengths"""
        all_words = []
        
        for length in lengths:
            print(f"📝 Fetching {count_per_length} words of length {length}...")
            words = self.fetch_random_words(length, count_per_length)
            all_words.extend(words)
            
        return all_words

    def load_checked_names(self):
        """Load previously checked names from file"""
        try:
            with open(self.checked_names_file, 'r') as f:
                checked_names = set(line.strip().lower() for line in f if line.strip())
            print(f"📋 Loaded {len(checked_names)} previously checked names")
            return checked_names
        except FileNotFoundError:
            print("📋 No previous checked names found - starting fresh")
            return set()
    
    def load_available_names(self):
        """Load previously found available names from file"""
        try:
            with open(self.available_names_file, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#') and not line.startswith('='):
                        # Parse format: "name (idle user)" or just "name"
                        parts = line.strip().split(' (')
                        name = parts[0]
                        is_idle = len(parts) > 1 and 'idle' in parts[1]
                        
                        self.available_names.append({
                            'name': name,
                            'available': True,
                            'belongs_to_idle_user': is_idle,
                            'status': 'loaded_from_file'
                        })
            print(f"✅ Loaded {len(self.available_names)} previously found available names")
        except FileNotFoundError:
            print("✅ No previous available names found - starting fresh")
    
    def save_checked_name(self, name):
        """Append a checked name to the file"""
        with open(self.checked_names_file, 'a') as f:
            f.write(f"{name.lower()}\n")
        self.checked_names_set.add(name.lower())
    
    def save_available_name(self, name_info):
        """Append an available name to the file"""
        idle_text = " (idle user)" if name_info['belongs_to_idle_user'] else ""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(self.available_names_file, 'a') as f:
            f.write(f"{name_info['name']}{idle_text} - Found: {timestamp}\n")
    
    def filter_unchecked_names(self, names_list):
        """Remove names that have already been checked"""
        unchecked = [name for name in names_list if name.lower() not in self.checked_names_set]
        skipped = len(names_list) - len(unchecked)
        
        if skipped > 0:
            print(f"📋 Skipping {skipped} already checked names")
            print(f"🎯 {len(unchecked)} new names to check")
        
        return unchecked
    
    def save_summary_report(self):
        """Save a summary report of all findings"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"faceit_summary_{timestamp}.txt"
        
        total_checked = len(self.checked_names_set)
        total_available = len(self.available_names)
        
        with open(filename, 'w') as f:
            f.write(f"FACEIT Name Availability Summary Report\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"📊 STATISTICS:\n")
            f.write(f"   Total names checked: {total_checked:,}\n")
            f.write(f"   Available names found: {total_available:,}\n")
            if total_checked > 0:
                success_rate = (total_available / total_checked) * 100
                f.write(f"   Success rate: {success_rate:.2f}%\n")
            f.write("\n")
            
            f.write(f"🎯 AVAILABLE NAMES ({total_available}):\n")
            f.write("-" * 40 + "\n")
            
            # Group by idle vs non-idle
            regular_names = []
            idle_names = []
            
            for name_info in self.available_names:
                if name_info.get('belongs_to_idle_user', False):
                    idle_names.append(name_info['name'])
                else:
                    regular_names.append(name_info['name'])
            
            if regular_names:
                f.write(f"\n🔥 FULLY AVAILABLE ({len(regular_names)}):\n")
                for name in sorted(regular_names):
                    f.write(f"   {name}\n")
            
            if idle_names:
                f.write(f"\n💤 IDLE USER NAMES ({len(idle_names)}):\n")
                for name in sorted(idle_names):
                    f.write(f"   {name}\n")
            
            f.write(f"\n📁 DATA FILES:\n")
            f.write(f"   Checked names: {self.checked_names_file}\n")
            f.write(f"   Available names: {self.available_names_file}\n")
        
        print(f"📋 Summary report saved to {filename}")
        return filename
    
    def print_progress(self):
        """Print current progress"""
        if self.total_count > 0:
            progress = (self.checked_count / self.total_count) * 100
            print(f"Progress: {self.checked_count}/{self.total_count} ({progress:.1f}%) - Available: {len(self.available_names)}")
    
    def run_check(self, names_list, initial_delay=1.0):
        """Run the availability check for a list of names with dynamic delay optimization"""
        # Filter out already checked names
        unchecked_names = self.filter_unchecked_names(names_list)
        
        if not unchecked_names:
            print("🎉 All names in this list have already been checked!")
            return
        
        self.total_count = len(unchecked_names)
        print(f"Starting check for {self.total_count} names...")
        print(f"🚀 Dynamic delay: Starting at {initial_delay}s, decreasing by 0.1s every 10 requests")
        print(f"⚡ Minimum delay: 0.5s to avoid rate limits")
        print("=" * 60)
        
        new_available_count = 0
        current_delay = initial_delay
        min_delay = 0.5
        
        for i, name in enumerate(unchecked_names):
            # Dynamically adjust delay - decrease by 0.1s every 10 requests
            if i > 0 and i % 10 == 0 and current_delay > min_delay:
                current_delay = max(min_delay, current_delay - 0.1)
                print(f"\n⚡ Speed optimized! New delay: {current_delay:.1f}s")
            
            # Show what we're checking
            delay_indicator = f"({current_delay:.1f}s)" if current_delay != initial_delay else ""
            print(f"[{i + 1:4d}/{self.total_count}] {delay_indicator} Checking: {name}...", end=" ")
            
            result = self.check_name_availability(name)
            
            # Check for rate limiting and adjust delay accordingly
            if result['status'] == 'error_429_rate_limit':
                current_delay = min(current_delay + 0.5, 3.0)  # Increase delay if rate limited
                print(f"⏱️  RATE LIMITED - increasing delay to {current_delay:.1f}s")
            elif result['status'] == 'error_403_blocked':
                current_delay = min(current_delay + 1.0, 5.0)  # Increase delay more for 403
                print(f"🚫 BLOCKED - increasing delay to {current_delay:.1f}s")
            else:
                # Save that we checked this name
                self.save_checked_name(name)
                
                if result['status'] == 'success':
                    if result['available']:
                        self.available_names.append(result)
                        self.save_available_name(result)
                        new_available_count += 1
                        idle_text = " (idle user)" if result['belongs_to_idle_user'] else ""
                        print(f"✅ AVAILABLE{idle_text}")
                    else:
                        print("❌ TAKEN")
                else:
                    print(f"⚠️  ERROR ({result['status']})")
            
            # Show summary progress every 25 checks
            if (i + 1) % 25 == 0:
                progress = ((i + 1) / self.total_count) * 100
                total_available = len(self.available_names)
                print(f"\n📊 Progress: {progress:.1f}% | New Available: {new_available_count} | Total Available: {total_available} | Current Speed: {current_delay:.1f}s")
                print("-" * 60)
            
            # Add dynamic delay
            time.sleep(current_delay)
        
        print(f"\n{'='*60}")
        print(f"✅ Check completed!")
        print(f"📈 Names checked this session: {self.total_count}")
        print(f"🆕 New available names found: {new_available_count}")
        print(f"🎯 Total available names: {len(self.available_names)}")
        print(f"⚡ Final delay: {current_delay:.1f}s (started at {initial_delay}s)")
        if new_available_count > 0:
            success_rate = (new_available_count / self.total_count) * 100
            print(f"📊 Success rate this session: {success_rate:.1f}%")

def main():
    print("FACEIT Name Availability Checker")
    print("=" * 40)
    
    # Need authentication cookies since you must be logged in
    print("🔑 FACEIT requires login to check name availability")
    print("📋 From your browser cookies (F12 → Application → Cookies), copy these values:")
    print("   • __Host-AuthSession")
    print("   • __Host-FaceitGatewayAuthorization") 
    print("   • cf_clearance")
    print()
    
    auth_session = input("__Host-AuthSession: ").strip()
    gateway_auth = input("__Host-FaceitGatewayAuthorization: ").strip()
    cf_clearance = input("cf_clearance: ").strip()
    
    if not auth_session or not gateway_auth:
        print("❌ AuthSession and GatewayAuthorization cookies are required")
        print("   Please get these cookies and run the script again")
        return
    
    # Build cookie string
    cookies = f"__Host-AuthSession={auth_session}; __Host-FaceitGatewayAuthorization={gateway_auth}"
    if cf_clearance:
        cookies += f"; cf_clearance={cf_clearance}"
    
    checker = FaceitNameChecker(cookies)
    
    # Test connection first
    print("\n🧪 Testing connection...")
    test_result = checker.check_name_availability("test")
    if test_result['status'] == 'success':
        print("✅ Connection successful!")
    elif 'error_403' in test_result['status']:
        print("❌ Still getting 403 errors - try providing cookies")
        return
    elif 'SSLError' in test_result['status'] or 'ConnectionError' in test_result['status']:
        print("🔒 SSL/Connection issue detected. Trying with SSL verification disabled...")
        # Disable SSL verification as fallback
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        checker.session.verify = False
        test_result = checker.check_name_availability("test")
        if test_result['status'] == 'success':
            print("✅ Connection successful with SSL verification disabled!")
        else:
            print(f"❌ Still failing: {test_result['status']}")
            return
    else:
        print(f"⚠️  Got status: {test_result['status']}")
        print("❓ Try running the script again or check your internet connection")
        return
    print("\n" + "=" * 40)
    print("1. Random English words (3-4 letters) - RECOMMENDED")
    print("2. Custom length words (5, 6, 7+ letters)")
    print("3. Check ALL 3-letter combinations (17,576 names)")
    print("4. Check ALL 4-letter combinations (456,976 names - VERY SLOW)")
    print("5. Custom list")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == "1":
        print("Fetching random English words from API...")
        names = checker.generate_random_word_combinations()
        if names:
            print("⚠️  Starting with 1-second delay, optimizing automatically")
            checker.run_check(names, initial_delay=1.0)
        else:
            print("Failed to fetch words from API. Try again later.")
    
    elif choice == "2":
        print("🎯 Custom Length Word Generator")
        print("Examples: 5 (for 5-letter words), 5,6,7 (for multiple lengths)")
        lengths_input = input("Enter word lengths (comma-separated): ").strip()
        
        try:
            lengths = [int(x.strip()) for x in lengths_input.split(',') if x.strip()]
            if not lengths:
                print("❌ No valid lengths provided")
                return
            
            # Validate lengths
            invalid_lengths = [l for l in lengths if l < 1 or l > 20]
            if invalid_lengths:
                print(f"❌ Invalid lengths: {invalid_lengths}. Must be between 1-20")
                return
            
            count_input = input(f"Words per length (default 1000): ").strip()
            count_per_length = int(count_input) if count_input else 1000
            
            print(f"📝 Fetching {count_per_length} words each for lengths: {lengths}")
            names = checker.generate_custom_length_words(lengths, count_per_length)
            
            if names:
                total_words = len(names)
                estimated_time = (total_words * 0.5) / 3600  # rough estimate in hours
                print(f"✅ Generated {total_words} words")
                print(f"⏱️  Estimated time: {estimated_time:.1f} hours")
                
                confirm = input("Continue with availability check? (y/n): ")
                if confirm.lower() == 'y':
                    checker.run_check(names, initial_delay=0.8)
            else:
                print("❌ Failed to fetch words from API. Try again later.")
                
        except ValueError:
            print("❌ Invalid input. Please enter numbers only (e.g., 5,6,7)")
            return
    
    elif choice == "3":
        print("Generating all 3-letter combinations...")
        names = checker.generate_3_letter_combinations()
        print(f"Generated {len(names)} combinations")
        confirm = input("This will take about 2.5 hours. Continue? (y/n): ")
        if confirm.lower() == 'y':
            checker.run_check(names, initial_delay=0.5)
    
    elif choice == "4":
        print("Generating all 4-letter combinations...")
        names = checker.generate_4_letter_combinations()
        print(f"Generated {len(names)} combinations")
        confirm = input("This will take about 60+ hours. Continue? (y/n): ")
        if confirm.lower() == 'y':
            checker.run_check(names, initial_delay=0.5)
    
    elif choice == "5":
        custom_names = input("Enter names separated by commas: ").strip().split(',')
        custom_names = [name.strip().lower() for name in custom_names if name.strip()]
        if custom_names:
            checker.run_check(custom_names, initial_delay=0.3)
    
    else:
        print("Invalid choice. Exiting.")
        return
    
    # Show final results and save summary
    print(f"\n{'='*60}")
    print("📁 PERSISTENT FILES CREATED/UPDATED:")
    print(f"   📋 Checked names: {checker.checked_names_file}")
    print(f"   ✅ Available names: {checker.available_names_file}")
    
    if checker.available_names:
        print(f"\n🎯 ALL AVAILABLE NAMES FOUND:")
        regular_names = []
        idle_names = []
        
        for name_info in checker.available_names:
            if name_info.get('belongs_to_idle_user', False):
                idle_names.append(name_info['name'])
            else:
                regular_names.append(name_info['name'])
        
        if regular_names:
            print(f"\n🔥 FULLY AVAILABLE ({len(regular_names)}):")
            for name in sorted(regular_names):
                print(f"   {name}")
        
        if idle_names:
            print(f"\n💤 IDLE USER NAMES ({len(idle_names)}):")
            for name in sorted(idle_names):
                print(f"   {name}")
        
        # Generate summary report
        summary_file = checker.save_summary_report()
        print(f"\n📋 Detailed summary saved to: {summary_file}")
    else:
        print("\n❌ No available names found in this session.")
    
    print(f"\n💡 TIP: Run the script again to continue where you left off!")
    print(f"   Your progress is automatically saved to {checker.checked_names_file}")

if __name__ == "__main__":
    main()

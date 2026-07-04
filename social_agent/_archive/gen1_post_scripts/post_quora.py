"""
Quora Answer Generator + Auto-poster for RankerToolAI.

Usage:
  python post_quora.py --generate-all   # Generate answers for all tools
  python post_quora.py --tool jasper     # Generate for one tool
  python post_quora.py --post            # Auto-post via Selenium (requires Chrome)
  python post_quora.py --status          # Show what's been generated
"""

import os, sys, json, time, random
from dotenv import load_dotenv
load_dotenv()

from content_generator import generate_quora_answer
from database import log_post, already_posted

DIR        = os.path.dirname(__file__)
TOOLS_FILE = os.path.join(DIR, "data", "tools.json")
OUTPUT_DIR = os.path.join(DIR, "data", "quora_answers")
os.makedirs(OUTPUT_DIR, exist_ok=True)

QUORA_QUESTIONS = {
    "elevenlabs":       ["What is the best AI voice generator in 2026?",
                         "Is ElevenLabs worth it for podcasting?",
                         "What are the best text-to-speech tools for content creators?"],
    "surfer-seo":       ["What is the best SEO content optimization tool?",
                         "Is Surfer SEO worth the money in 2026?",
                         "How do I rank my blog posts faster on Google?"],
    "jasper":           ["What is the best AI writing tool for marketing?",
                         "Is Jasper AI worth it for content marketing?",
                         "What are the best AI tools for copywriting?"],
    "semrush":          ["What is the best SEO tool for beginners?",
                         "Is Semrush better than Ahrefs?",
                         "What tools do professional SEOs use?"],
    "writesonic":       ["What is the best affordable AI writing tool?",
                         "How does Writesonic compare to ChatGPT for content?",
                         "What are good free AI writing tools?"],
    "stable-diffusion": ["What is the best free AI image generator?",
                         "How do I get started with Stable Diffusion?",
                         "Is Stable Diffusion better than Midjourney?"],
    "canva-ai":         ["What are the best AI design tools for non-designers?",
                         "Is Canva AI worth upgrading to Pro?",
                         "What is the easiest AI tool for social media graphics?"],
    "grok":             ["Is Grok AI better than ChatGPT?",
                         "What can Grok do that other AI chatbots cannot?",
                         "Is X Premium worth it for Grok access?"],
    "runway":           ["What is the best AI video generator in 2026?",
                         "Is Runway ML worth it for video creators?",
                         "How do I create AI videos for YouTube?"],
    "cursor":           ["What is the best AI coding assistant in 2026?",
                         "Is Cursor better than GitHub Copilot?",
                         "What AI tools do professional developers use?"],
}


def get_answer_path(slug, question_idx):
    return os.path.join(OUTPUT_DIR, f"{slug}_q{question_idx+1}.txt")


def generate_and_save(tool, question, question_idx):
    path = get_answer_path(tool["slug"], question_idx)
    if os.path.exists(path):
        print(f"  [skip] {tool['name']} Q{question_idx+1} — already generated")
        return True

    print(f"  Generating: {tool['name']} — {question[:60]}...")
    try:
        answer = generate_quora_answer(tool, question)
        search_url = "https://www.quora.com/search?q=" + question.replace(" ", "+")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"TOOL: {tool['name']}\n")
            f.write(f"QUESTION: {question}\n")
            f.write(f"SEARCH URL: {search_url}\n")
            f.write(f"STATUS: pending\n")
            f.write("=" * 60 + "\n\n")
            f.write(answer)
        print(f"  Saved: {os.path.basename(path)}")
        return True
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def generate_all(tools):
    total = sum(len(QUORA_QUESTIONS.get(t["slug"], [])) for t in tools)
    done = 0
    print(f"\nGenerating {total} Quora answers...\n")
    for tool in tools:
        questions = QUORA_QUESTIONS.get(tool["slug"], [])
        if not questions:
            continue
        print(f"[{tool['name']}]")
        for i, q in enumerate(questions):
            ok = generate_and_save(tool, q, i)
            if ok:
                done += 1
            time.sleep(1)
    print(f"\nDone: {done}/{total} answers ready in data/quora_answers/")


def show_status(tools):
    print("\n=== QUORA ANSWERS STATUS ===\n")
    total = 0
    generated = 0
    for tool in tools:
        questions = QUORA_QUESTIONS.get(tool["slug"], [])
        tool_done = 0
        for i, q in enumerate(questions):
            total += 1
            path = get_answer_path(tool["slug"], i)
            if os.path.exists(path):
                with open(path, encoding="utf-8") as f:
                    content = f.read()
                status = "posted" if "STATUS: posted" in content else "ready"
                tool_done += 1
                generated += 1
            else:
                status = "not generated"
            print(f"  {tool['name']:<20} Q{i+1}: [{status}]  {q[:50]}")
    print(f"\nTotal: {generated}/{total} generated")


def _wait_for(driver, by, selector, timeout=10):
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
    except Exception:
        return None


def _click_answer_button(driver):
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    # Try multiple selectors for the Answer button
    selectors = [
        (By.XPATH, "//button[normalize-space()='Answer']"),
        (By.XPATH, "//button[contains(@class,'answer') or contains(@class,'Answer')]"),
        (By.XPATH, "//*[contains(text(),'Answer this question')]"),
        (By.CSS_SELECTOR, "button[data-testid='answer-button']"),
    ]
    for by, sel in selectors:
        try:
            btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((by, sel)))
            btn.click()
            return True
        except Exception:
            continue
    return False


def _type_answer(driver, text):
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import pyperclip

    selectors = [
        "[contenteditable='true']",
        "[role='textbox']",
        ".notranslate[contenteditable]",
    ]
    for sel in selectors:
        try:
            editor = WebDriverWait(driver, 8).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, sel))
            )
            editor.click()
            time.sleep(0.5)
            # Use clipboard paste for reliable text insertion
            try:
                import pyperclip
                pyperclip.copy(text)
                import pyautogui
                pyautogui.hotkey('ctrl', 'v')
            except Exception:
                # Fallback: send_keys in chunks
                for chunk in [text[i:i+200] for i in range(0, len(text), 200)]:
                    editor.send_keys(chunk)
                    time.sleep(0.1)
            return True
        except Exception:
            continue
    return False


def _submit_answer(driver):
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    selectors = [
        (By.XPATH, "//button[normalize-space()='Submit']"),
        (By.XPATH, "//button[normalize-space()='Post']"),
        (By.XPATH, "//button[contains(@class,'submit') or contains(@class,'Submit')]"),
        (By.CSS_SELECTOR, "button[data-testid='submit-button']"),
    ]
    for by, sel in selectors:
        try:
            btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((by, sel)))
            btn.click()
            return True
        except Exception:
            continue
    return False


def auto_post_selenium(tools):
    """Post answers via Selenium browser automation."""
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
    except ImportError:
        print("Run: pip install selenium webdriver-manager")
        return

    profile_dir = os.path.join(DIR, "data", "quora_chrome_profile")
    os.makedirs(profile_dir, exist_ok=True)

    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={profile_dir}")
    options.add_argument("--no-sandbox")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    try:
        # Wait for Quora login
        driver.get("https://www.quora.com")
        time.sleep(4)
        if "login" in driver.current_url.lower():
            print("Chrome da mo - hay dang nhap Quora roi script tu dong tiep tuc (toi da 120 giay)...")
            for _ in range(60):
                time.sleep(2)
                if "login" not in driver.current_url.lower():
                    print("Da dang nhap thanh cong!")
                    break
            else:
                print("Timeout - khong phat hien dang nhap")
                driver.quit()
                return
        else:
            print("Da dang nhap Quora san!")

        time.sleep(2)
        posted_count = 0

        for tool in tools:
            questions = QUORA_QUESTIONS.get(tool["slug"], [])
            for i, question in enumerate(questions):
                path = get_answer_path(tool["slug"], i)
                if not os.path.exists(path):
                    continue

                with open(path, encoding="utf-8") as f:
                    content = f.read()

                if "STATUS: posted" in content:
                    print(f"[Quora] {tool['name']} Q{i+1}: da post roi, bo qua")
                    continue

                answer_text = content.split("=" * 60)[-1].strip()
                search_url = (
                    "https://www.quora.com/search?q="
                    + question.replace(" ", "+")
                    + "&type=question"
                )

                print(f"\n[Quora] Tim kiem: {question[:60]}")

                try:
                    driver.get(search_url)
                    time.sleep(3)

                    # Find first question link in search results
                    question_links = driver.find_elements(
                        By.XPATH,
                        "//a[contains(@href,'/') and .//span[string-length(text())>10]]"
                    )
                    # Filter for actual question links (Quora question URLs contain multiple words)
                    q_link = None
                    for el in question_links:
                        href = el.get_attribute("href") or ""
                        if "quora.com/" in href and "/profile" not in href and "/topic" not in href:
                            q_link = el
                            break

                    if not q_link:
                        print(f"[Quora] Khong tim thay cau hoi, bo qua")
                        continue

                    q_url = q_link.get_attribute("href")
                    print(f"[Quora] Mo cau hoi: {q_url[:80]}")
                    driver.get(q_url)
                    time.sleep(3)

                    # Click Answer button
                    if not _click_answer_button(driver):
                        print(f"[Quora] Khong tim thay nut Answer")
                        continue

                    time.sleep(2)

                    # Type answer
                    if not _type_answer(driver, answer_text):
                        print(f"[Quora] Khong the nhap noi dung")
                        continue

                    time.sleep(2)

                    # Submit
                    if not _submit_answer(driver):
                        print(f"[Quora] Khong tim thay nut Submit")
                        continue

                    time.sleep(3)

                    # Mark as posted
                    updated = content.replace("STATUS: pending", "STATUS: posted")
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(updated)

                    log_post("quora", tool["slug"], q_url)
                    posted_count += 1
                    print(f"[Quora] POSTED: {tool['name']} Q{i+1}")

                    # Random delay between posts (30-90 seconds)
                    wait_sec = random.randint(30, 90)
                    print(f"[Quora] Doi {wait_sec}s truoc bai tiep theo...")
                    time.sleep(wait_sec)

                except Exception as e:
                    print(f"[Quora] Loi {tool['name']} Q{i+1}: {str(e)[:100]}")
                    time.sleep(5)
                    continue

    finally:
        try:
            driver.quit()
        except Exception:
            pass

    print(f"\nHoan thanh: {posted_count} cau tra loi da post")


def main():
    with open(TOOLS_FILE, encoding="utf-8") as f:
        tools = json.load(f)

    if "--status" in sys.argv:
        show_status(tools)
    elif "--post" in sys.argv:
        auto_post_selenium(tools)
    elif "--tool" in sys.argv:
        idx = sys.argv.index("--tool")
        slug = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else None
        if slug:
            matches = [t for t in tools if t["slug"] == slug]
            if matches:
                questions = QUORA_QUESTIONS.get(slug, [])
                print(f"[{matches[0]['name']}]")
                for i, q in enumerate(questions):
                    generate_and_save(matches[0], q, i)
                    time.sleep(1)
    else:
        generate_all(tools)


if __name__ == "__main__":
    main()

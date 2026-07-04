import os
import time
import random
from content_generator import generate_quora_answer
from database import log_post, already_posted

QUORA_QUESTIONS = {
    "elevenlabs": [
        "What is the best AI voice generator in 2026?",
        "Is ElevenLabs worth it for podcasting?",
        "What are the best text-to-speech tools for content creators?"
    ],
    "surfer-seo": [
        "What is the best SEO content optimization tool?",
        "Is Surfer SEO worth the money in 2026?",
        "How do I rank my blog posts faster on Google?"
    ],
    "jasper": [
        "What is the best AI writing tool for marketing?",
        "Is Jasper AI worth it for content marketing?",
        "What are the best AI tools for copywriting?"
    ],
    "semrush": [
        "What is the best SEO tool for beginners?",
        "Is Semrush better than Ahrefs?",
        "What tools do professional SEOs use?"
    ],
    "writesonic": [
        "What is the best affordable AI writing tool?",
        "How does Writesonic compare to ChatGPT for content?",
        "What are good free AI writing tools?"
    ],
    "stable-diffusion": [
        "What is the best free AI image generator?",
        "How do I get started with Stable Diffusion?",
        "Is Stable Diffusion better than Midjourney?"
    ],
    "canva-ai": [
        "What are the best AI design tools for non-designers?",
        "Is Canva AI worth upgrading to Pro?",
        "What is the easiest AI tool for social media graphics?"
    ],
    "grok": [
        "Is Grok AI better than ChatGPT?",
        "What can Grok do that other AI chatbots cannot?",
        "Is X Premium worth it for Grok access?"
    ],
    "runway": [
        "What is the best AI video generator in 2026?",
        "Is Runway ML worth it for video creators?",
        "How do I create AI videos for YouTube?"
    ],
    "cursor": [
        "What is the best AI coding assistant in 2026?",
        "Is Cursor better than GitHub Copilot?",
        "What AI tools do professional developers use?"
    ]
}

def post(tool):
    if already_posted("quora", tool["slug"], days=7):
        print(f"[Quora] Already posted {tool['name']} this week, skipping")
        return

    questions = QUORA_QUESTIONS.get(tool["slug"], tool.get("quora_topics", []))
    if not questions:
        return

    question = random.choice(questions)

    try:
        # Generate the answer
        answer = generate_quora_answer(tool, question)

        # Selenium automation for Quora posting
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            options = webdriver.ChromeOptions()
            options.add_argument("--user-data-dir=" + os.path.expanduser("~/.quora_profile"))

            driver = webdriver.Chrome(options=options)
            driver.get("https://www.quora.com")
            time.sleep(3)

            # Save answer to file for manual posting if selenium fails
            save_for_manual(tool, question, answer)
            driver.quit()

        except ImportError:
            save_for_manual(tool, question, answer)

        log_post("quora", tool["slug"], "answer", status="manual", error=f"Q: {question}")
        return None

    except Exception as e:
        log_post("quora", tool["slug"], "answer", status="error", error=str(e))
        print(f"[Quora] Error: {e}")
        return None


def save_for_manual(tool, question, answer):
    """Save generated answers to a file for manual posting"""
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "manual_posts")
    os.makedirs(output_dir, exist_ok=True)

    filename = os.path.join(output_dir, f"quora_{tool['slug']}_{int(time.time())}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"QUORA ANSWER\n")
        f.write(f"Tool: {tool['name']}\n")
        f.write(f"Question: {question}\n")
        f.write(f"Search on Quora: https://www.quora.com/search?q={question.replace(' ', '+')}\n")
        f.write(f"\n{'='*60}\n\n")
        f.write(answer)

    print(f"[Quora] Answer saved for manual posting: {filename}")

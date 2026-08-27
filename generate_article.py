#!/usr/bin/env python3
import os, json, random, datetime, httpx
from pathlib import Path

HF_TOKEN = os.environ.get("HF_TOKEN", "")
MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

TOPICS = [
    "5 astuces pour automatiser son trading de crypto",
    "Comment gagner du temps avec Python en 2025",
    "Les meilleures stratégies de contenu passif",
    "Pourquoi le dropshipping n'est plus rentable",
    "Guide débutant pour coder un bot Telegram",
]

def generate_article(topic: str) -> str:
    prompt = (
        f"Tu es un blogueur expert en revenus passifs. "
        f"Écris un article de blog en français, 500-800 mots, "
        f"sur le thème suivant : {topic}. "
        f"Inclus des titres (##), des listes, et des mots-clés en **gras**. "
        f"Termine par une conclusion et un appel à l'action."
    )
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 1024, "temperature": 0.7, "do_sample": True},
    }
    try:
        with httpx.Client(timeout=120) as client:
            resp = client.post(
                f"https://api-inference.huggingface.co/models/{MODEL}",
                headers=headers, json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, list) and data:
                text = data[0].get("generated_text", "")
                if text.startswith(prompt):
                    text = text[len(prompt):].strip()
                return text
            return f"Erreur réponse : {json.dumps(data, indent=2)}"
    except Exception as e:
        return f"Erreur API : {e}"

def save_article(markdown: str, topic: str) -> Path:
    today = datetime.date.today()
    slug = topic.lower().replace(" ", "-")[:50]
    filename = f"{today.isoformat()}-{slug}.md"
    posts_dir = Path("_posts")
    posts_dir.mkdir(exist_ok=True)
    filepath = posts_dir / filename
    front_matter = f"""---
layout: post
title: "{topic}"
date: {today.isoformat()}
categories: blog
---
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(front_matter)
        f.write(markdown)
    return filepath

def main():
    topic = random.choice(TOPICS)
    print(f"[INFO] Génération : {topic}")
    article = generate_article(topic)
    path = save_article(article, topic)
    print(f"[OK] Sauvegardé : {path}")

if __name__ == "__main__":
    main()

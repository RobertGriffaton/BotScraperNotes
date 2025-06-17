print("Début du script Python")
import discord
from discord.ext import commands, tasks
from selenium import webdriver
from selenium.webdriver.common.by import By
import asyncio
import os
import json
import time

# --------- CONFIGURATION ---------
TOKEN = '***********'
CHANNEL_ID = 1384563825260367872
IUT_URL = 'https://etudnotes.iutv.univ-paris13.fr/'
USERNAME = '******'
PASSWORD = '*********'
NOTES_FILE = "notes_connues.json"
CHECK_INTERVAL = 60 * 15  # 1h
custom_tag = "releve-but"
# ---------------------------------

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def fetch_notes():
    print("Scraping des notes par paires...")
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get(IUT_URL)
    driver.find_element(By.ID, "username").send_keys(USERNAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.ID, "submit").click()
    time.sleep(8)

    notes_list = []
    try:
        releve_elem = driver.find_element(By.TAG_NAME, custom_tag)
        shadow_root = driver.execute_script('return arguments[0].shadowRoot', releve_elem)
        main_section = shadow_root.find_element(By.CSS_SELECTOR, "main")
        sections = main_section.find_elements(By.TAG_NAME, "section")
        notes_section = sections[3] if len(sections) > 3 else sections[-1]
        divs = notes_section.find_elements(By.TAG_NAME, "div")

        texts = [div.text.strip() for div in divs if div.text.strip()]
        i = 0
        while i < len(texts) - 1:
            nom = texts[i]
            val = texts[i+1].split('\n')[0].replace(',', '.')
            # On garde que les couples [matière][note]
            try:
                note_value = float(val)
                if (
                    not any(x in nom for x in ["Moyenne", "Rang", "Bonus", "Malus", "ECTS", "~", "UE", "Coef", ":"])
                    and len(nom) > 2  # évite les lignes vides ou mini
                    and 0 <= note_value <= 20
                ):
                    notes_list.append({"nom": nom, "note": f"{note_value:.2f}"})
            except:
                pass
            i += 1
        if not notes_list:
            print("DEBUG : Toujours 0 notes - envoie-moi un copié-collé de 10 lignes DEBUG à la suite (sans rien retirer) pour que je voie la séquence.")
    except Exception as e:
        print("Erreur lors de la récupération du shadow DOM :", e)
    driver.quit()
    print(f"{len(notes_list)} notes filtrées trouvées.")
    return notes_list




def load_known_notes():
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "r") as f:
            return json.load(f)
    return []

def save_known_notes(notes):
    with open(NOTES_FILE, "w") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)

def get_new_notes(all_notes, known_notes):
    known_set = {(n["nom"], n["note"]) for n in known_notes}
    return [n for n in all_notes if (n["nom"], n["note"]) not in known_set]

def split_message(msg, max_length=1900):
    # Découpe le message pour ne pas dépasser la limite de Discord (2000)
    lines = msg.split('\n')
    chunks = []
    chunk = ""
    for line in lines:
        # Si une ligne seule est trop longue, on la coupe brute
        while len(line) > max_length:
            chunks.append(line[:max_length])
            line = line[max_length:]
        if len(chunk) + len(line) + 1 > max_length:
            chunks.append(chunk)
            chunk = ""
        chunk += line + "\n"
    if chunk:
        chunks.append(chunk)
    return chunks


@bot.event
async def on_ready():
    print(f'Bot connecté en tant que {bot.user}')
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send("Le bot de surveillance de notes est actif ! 📢")
    check_notes.start()

@tasks.loop(seconds=CHECK_INTERVAL)
async def check_notes():
    channel = bot.get_channel(CHANNEL_ID)
    all_notes = fetch_notes()
    known_notes = load_known_notes()
    new_notes = get_new_notes(all_notes, known_notes)
    # Pour ne pas spam Discord, batch les notifications
    BATCH_SIZE = 10
    if new_notes:
        if len(new_notes) > BATCH_SIZE:
            await channel.send(f"{len(new_notes)} nouvelles notes détectées. Voici les {BATCH_SIZE} premières :")
            batch = new_notes[:BATCH_SIZE]
        else:
            batch = new_notes
        for note in batch:
            txt = f"Nouvelle note ajoutée : **{note['nom']}** — **{note['note']}**"
            if len(txt) > 2000:
                txt = txt[:1997] + "..."
            await channel.send(txt)
        if len(new_notes) > BATCH_SIZE:
            await channel.send("... (le reste des notes est disponible avec !notes)")
        known_notes.extend(new_notes)
        save_known_notes(known_notes)

@bot.command()
async def notes(ctx):
    """Commande Discord !notes pour afficher toutes tes notes"""
    all_notes = fetch_notes()
    if not all_notes:
        await ctx.send("Aucune note trouvée pour l’instant.")
        return
    msg = "**Voici toutes tes notes actuelles :**\n"
    for note in all_notes:
        msg += f"• **{note['nom']}** : {note['note']}\n"
    # Découpe et envoie en plusieurs messages si besoin
    for chunk in split_message(msg, 1800):
        await ctx.send(chunk)

if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except Exception as e:
        print("Erreur au lancement du bot :", e)
        import traceback
        traceback.print_exc()
        input("Appuie sur Entrée pour quitter...")

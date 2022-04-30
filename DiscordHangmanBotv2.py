# bot.py
import os
import discord
import random
import re
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='k.')

guessed_letters = []
game_status = False
hm_word = ""
guess_number = 0
word_list_hard = []
word_list_easy = []


@bot.event
async def on_ready():
    print(f"{bot.user} is connected to Discord!")
    hard_wordlist = open('HMWordsHard.txt', 'r')
    easy_wordlist = open('HMWordsEasy.txt', 'r')
    for word in hard_wordlist:
        word_list_hard.append(word.strip())
    for word in easy_wordlist:
        word_list_easy.append(word.strip())
    hard_wordlist.close()
    easy_wordlist.close()


@bot.event
async def on_member_join(member):
    print(f"{member}has joined the discord.")


@bot.command(name='hm', help="""
**This bot is currently in development and being tested by a highly unprofessional crew.**

Hangman is a program where a random word is selected from a predefined and editable list.

You can use k.hmeasy to begin a game with an "easy" word or k.hmhard to begin a game with a "hard" word.

The words are separated and defined by their usage of common (such as e, a, r) or uncommon (such as x, q, z) letters and how often they are used in daily language.

You have 7 chances (may be altered in the future) to guess a letter in the word.  Each incorrect guess takes away 1 chance and adds a piece of the hangman.

Once the hangman is fully pieced together and hanged the game is over.

**Can you save the hangman?***
""")


async def hm(ctx):
    response = "Please type k.help hm for instructions or k.hmeasy/k.hmhard to begin a game."
    await ctx.send(response)


@bot.command(name="hmeasy", help="Begins a game of hangman using the easy word list.")
async def hm_easy(ctx):
    hm_channel = ctx.channel.id
    print("The channel ID is:", hm_channel)
    author = ctx.author
    guild = ctx.guild
    game_on = start_game()
    if not game_on:
        global hm_word
        hm_word = random.choice(word_list_easy)
        await  process1(hm_channel, author, guild)
        return hm_word, hm_channel
    elif game_on:
        await ctx.send("A game of hangman has already started, please finish it before starting a new one.")


@bot.command(name="hmhard", help="Begins a game of hangman using the hard word list.")
async def hm_hard(ctx):
    hm_channel = ctx.channel.id
    print("The channel ID is:", hm_channel)
    author = ctx.author
    guild = ctx.guild
    game_on = start_game()
    if not game_on:
        global hm_word
        hm_word = random.choice(word_list_hard)
        await process1(hm_channel, author, guild)
        return hm_word, hm_channel
    elif game_on:
        await ctx.send("A game of hangman has already started, please finish it before starting a new one.")


async def process1(hm_channel, author, guild):
    num_of_characters = number_of_characters(hm_word)
    print(num_of_characters)
    print("The word is:", hm_word)
    channel = bot.get_channel(hm_channel)
    await channel.send("A game of hangman has started!  Can " + str(author.mention) + " and the rest of " + str(guild) + " save the hangman?")
    embed1 = await create_embed_1(hm_word, number_of_characters(hm_word))
    gallowsimg_0 = gallow_img(guess_number)
    await channel.send(file=gallowsimg_0, embed=embed1)
    return hm_word


@bot.command(name="hml", help="Allows you to guess a single letter.")
async def letter_guess(ctx):
    hml_channel = ctx.channel.id
    global guess_number
    if not game_status:
        await ctx.send("Please start a game before guessing letters!")
    else:
        while True:
            guess = ctx.message.content
            try:
                letter = re.search('k\.hml\s*([a-z])$', guess, re.I).group(1)
                if letter in guessed_letters:
                    await ctx.send("You have already guessed the letter '" + str(letter) + "', try another.")
                    break
                elif str(letter) in hm_word:
                    new_noc = replace_uscore(letter, hm_word, guessed_letters)
                    gallows_print = create_gallows(guess_number, new_num_of_chars)
                    gallows_img = gallow_img(guess_number)
                    await ctx.send(file=gallows_img, embed=gallows_print)
                    await wincon(new_num_of_chars, hm_word, hml_channel)
                    break
                else:
                    new_noc = replace_uscore(letter, hm_word, guessed_letters)
                    guess_number += 1
                    gallows_print = create_gallows(guess_number, new_num_of_chars)
                    gallows_img = gallow_img(guess_number)
                    await ctx.send(file=gallows_img, embed=gallows_print)
                    await wincon(new_num_of_chars, hm_word, hml_channel)
                    return guess_number
            except AttributeError:
                await ctx.send("Please guess only a single letter.")
                break


def replace_uscore(letter, hm_word, guessed_letters):
    global new_num_of_chars
    new_num_of_chars = ""
    guessed_letters.append(letter)
    for character in hm_word.strip():
        if character in guessed_letters:
            new_num_of_chars += (character + " ")
        else:
            new_num_of_chars += "\_ "
    return new_num_of_chars


def number_of_characters(hm_word):
    num_of_characters = ""
    for character in hm_word.strip():
        if character == " ":
            num_of_characters += " "
        elif character != " ":
            num_of_characters += "\_ "
    return num_of_characters


def start_game():
    global game_status
    if not game_status:
        game_status = True
        return False
    elif game_status is True:
        return True


async def create_embed_1(hm_word, num_of_characters):
    # Embed 1
    embed1 = discord.Embed(title="The Gallows")
    embed1.set_image(url="attachment://image0.jpg")
    embed1.add_field(name="\u200b", value="Your word has " + str(len(hm_word)) + " letters.", inline=False)
    embed1.add_field(name="\u200b", value="\u200b{}".format(num_of_characters), inline=False)
    embed1.add_field(name="\u200b", value="Please guess your first letter.", inline=False)
    return embed1


async def wincon(new_num_of_chars, hm_word, hml_channel):
    wincon = ""
    for character in new_num_of_chars:
        if character != " ":
            wincon += character
    if wincon == hm_word.strip():
        await bot.get_channel(hml_channel).send("Congratulations!  You guessed the word and saved the hangman!")
        game_over()
    elif guess_number == 8:
        await bot.get_channel(hml_channel).send("Oh no!  The word was " + hm_word.strip() + ".  You failed to save the hangman!")
        game_over()


def gallow_img(guess_number):
    gallows_img = discord.File("KamGaming/Hangman{}.jpg".format(guess_number), filename="image{}.jpg".format(guess_number))
    return gallows_img


def create_gallows(guess_number, new_num_of_chars):
    embed_gallows = discord.Embed(title="The Gallows")
    embed_gallows.set_image(url='attachment://image{}.jpg'.format(guess_number))
    embed_gallows.add_field(name="Letters you have guessed", value=str(guessed_letters), inline=False)
    embed_gallows.add_field(name="\u200b", value=new_num_of_chars, inline=False)
    return embed_gallows


def game_over():
    global game_status
    global hm_word
    global guessed_letters
    global guess_number
    game_status = False
    hm_word = ""
    guessed_letters = []
    guess_number = 0


@bot.command(name="hmstop", help="Stops and restarts the game.")
async def stop(ctx):
    if game_status is False:
        await ctx.send("There is no game to stop!")
    else:
        game_over()
        await ctx.send("The game of hangman has been stopped and restarted.")


bot.run(TOKEN)

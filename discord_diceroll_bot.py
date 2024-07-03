import re
import random
import logging
import json
from datetime import datetime
from hashlib import sha256
import discord
from discord.ext import commands

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("logs/bot.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Function to load messages from JSON file
def load_messages():
    try:
        with open('messages.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error("messages.json file not found")
        return {}
    except json.JSONDecodeError:
        logger.error("JSON decoding error in messages.json")
        return {}

# Load messages
messages = load_messages()

# Initialize the bot with intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Handle /start command
@bot.command(name='start')
async def start(ctx):
    await ctx.send(messages.get('start', 'Error loading message'))

# Handle /info command
@bot.command(name='info')
async def info(ctx):
    await ctx.send(messages.get('help', 'Error loading message'))

# Function to parse dice expressions
def parse_dice_expression(expression):
    dice_pattern = re.compile(r'(\d*)d(\d+)|([+-]\d+)')
    return dice_pattern.findall(expression)

# Function to evaluate dice expressions
def evaluate_expression(matches):
    total = 0
    results = []
    modifier = 0

    for match in matches:
        if match[0] or match[1]:  # If it's a dice expression, e.g., 2d6
            num_dice = int(match[0]) if match[0] else 1
            dice_size = int(match[1])
            dice_results = [random.randint(1, dice_size) for _ in range(num_dice)]
            results.extend(dice_results)
            total += sum(dice_results)
        elif match[2]:  # If it's a modifier, e.g., +3
            modifier += int(match[2])
            total += int(match[2])

    return total, results, modifier

# Handle /roll command
@bot.command(name='roll')
async def roll(ctx, *, dice_expression="1d20"):
    try:
        # Use user ID and message ID to initialize random seed
        user_id = ctx.message.author.id
        message_id = ctx.message.id
        seed_value = sha256(f"{datetime.now().timestamp()}_{user_id}_{message_id}".encode()).hexdigest()
        random.seed(int(seed_value, 16))

        matches = parse_dice_expression(dice_expression)

        if not matches:
            await ctx.send(messages.get('invalid_format', 'Error loading message'))
            return

        total, results, modifier = evaluate_expression(matches)
        results_str = ", ".join(map(str, results))
        modifier_str = f" + {modifier}" if modifier else ""

        await ctx.send(
            messages.get('roll_result', 'Error loading message').format(
                dice_expression=dice_expression, results_str=results_str, modifier_str=modifier_str, total=total)
        )

    except Exception as e:
        logger.error(f"{messages.get('log_error', 'Error processing /roll command')}: {e}")
        await ctx.send(messages.get('error', 'Error loading message'))

def main():
    # Run the bot
    bot.run('YOUR_DISCORD_BOT_TOKEN')

if __name__ == '__main__':
    main()

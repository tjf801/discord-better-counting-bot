import asyncio
import os
import discord
from discord.message import Message
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

@client.event
async def on_ready():
	print(f'{client.user} has connected to Discord!')

count = 0
last_sender = None
record = open("record.txt", "r+")
top_count = int(record.read())
LOCK = asyncio.Lock()

@client.event
async def on_message(message: Message):
	if message.author == client.user or message.channel.name!='counting': return
	async with LOCK:
		global count, last_sender, record, top_count
		
		import math
		SAFEBUILTINS = {
			'type': type,
			'int': int,
			'float': float,
			'complex': complex,
			'str': str,
			'bool': bool,
			'slice': slice,
			'tuple': tuple,
			'list': list,
			'dict': dict,
			'set': set,
			'frozenset': frozenset,
			'enumerate': enumerate,
			'range': range,
			'property': property,
			
			'NotImplemented': NotImplemented,
			'Ellipsis': Ellipsis,
			
			'abs': abs,
			'all': all,
			'any': any,
			'ascii': ascii,
			'bin': bin,
			'callable': callable,
			'chr': chr,
			'dir': dir,
			'divmod': divmod,
			'filter': filter,
			'format': format,
			'getattr': getattr,
			'hasattr': hasattr,
			'hash': hash,
			'hex': hex,
			'id': id,
			'iter': iter,
			'isinstance': isinstance,
			'issubclass': issubclass,
			'len': len,
			'map': map,
			'max': max,
			'min': min,
			'next': next,
			'oct': oct,
			'ord': ord,
			'pow': pow,
			'reversed': reversed,
			'repr': repr,
			'round': round,
			'setattr': setattr,
			'sorted': sorted,
			'sum': sum,
			'zip': zip,
			
			'e': math.e,
			'inf': math.inf,
			'nan': math.nan,
			'π': math.pi,
			'pi': math.pi,
			'τ': math.tau,
			'tau': math.tau,
			
			'acos': math.acos,
			'acosh': math.acosh,
			'asin': math.asin,
			'asinh': math.asinh,
			'atan': math.atan,
			'atanh': math.atanh,
			'ceil': math.ceil,
			'copysign': math.copysign,
			'cos': math.cos,
			'cosh': math.cosh,
			'degrees': math.degrees,
			'erf': math.erf,
			'erfc': math.erfc,
			'exp': math.exp,
			'expm1': math.expm1,
			'fabs': math.fabs,
			'factorial': math.factorial,
			'floor': math.floor,
			'fmod': math.fmod,
			'frexp': math.frexp,
			'fsum': math.fsum,
			'gamma': math.gamma,
			'gcd': math.gcd,
			'hypot': math.hypot,
			'isclose': math.isclose,
			'isinf': math.isinf,
			'isfinite': math.isfinite,
			'isnan': math.isnan,
			'ldexp': math.ldexp,
			'lgamma': math.lgamma,
			'ln': lambda x: math.log(x),
			'log': math.log,
			'log2': math.log2,
			'log10': math.log10,
			'log1p': math.log1p,
			'modf': math.modf,
			'pow': math.pow,
			'radians': math.radians,
			'remainder': math.remainder,
			'sin': math.sin,
			'sinh': math.sinh,
			'sqrt': math.sqrt,
			'tan': math.tan,
			'tanh': math.tanh,
			'trunc': math.trunc,
			
		}
		if message.content[0] in '0123456789jeπ.-~([{' or message.content[:3]=="!c ":
			if message.content[:3]=="!c ":
				text = message.content[3:]
			else:
				#finds the longest piece of valid python code at the beginning to run
				for i in range(1, len(message.content)+1):
					try:
						compile(message.content[:1-i if 1-i!=0 else len(message.content)], "compile", "eval")
						break
					except: pass
				else: pass
				text = message.content[:1-i if 1-i!=0 else len(message.content)]
			
			try:
				result = eval(text, {'__builtins__': SAFEBUILTINS})
				if result == count + 1:
					if message.author == last_sender:
						if count!=0:
							await message.add_reaction("❌")
							await message.channel.send(f"{message.author.mention} RUINED IT AT **{count}**!! Next number is **1**. **You can't count two numbers in a row.**")
							count, last_sender = 0, None
						if count > top_count:
							top_count = count
							record.seek(0)
							record.write(str(top_count))
					else:
						if count >= top_count:
							await message.add_reaction("✔️")
							count, last_sender = count + 1, message.author
						else:
							await message.add_reaction("✅")
							count, last_sender = count + 1, message.author
				else:
					if count!=0:
						await message.add_reaction("❌")
						await message.channel.send(f"{message.author.mention} RUINED IT AT **{count}**!! Next number is **1**. **\"{result}\" is the wrong number.**")
						if count > top_count:
							top_count = count
							record.seek(0)
							record.write(str(top_count))
						count, last_sender = 0, None
			except Exception as e:
				if count!=0:
					if message.content[:3]=="!c ":
						await message.channel.send(f"{message.author.mention} RUINED IT AT **{count}**!! Next number is **1**. **{message.author.mention} is bad at programming.**\n`{str(e)}`")
					else:
						await message.channel.send(f"{message.author.mention} RUINED IT AT **{count}**!! Next number is **1**.\n`{str(e)}`")
					if count > top_count:
						top_count = count
						record.seek(0)
						record.write(str(top_count))
					count, last_sender = 0, None

client.run(TOKEN)
import discord
import os
import reverse_geocoder
from assets.country_code import find_country
from assets.facts import random_fact
from time import strftime, sleep
import requests
client = discord.Client()
from keep_alive import keep_alive
from ast import literal_eval
from replit import db
import json
import random
api_key = os.environ['api_key']
api_key2 = os.environ['api_key2']
@client.event
async def on_ready():
	print('We have logged in as {0.user}'.format(client))

@client.event
async def on_guild_join(guild):
  embed = discord.Embed(title = 'Ooh, looks really lovely in here.', description = 'Thanks for inviting us in! I\'ll be here to help. Use `.help` to begin.', color = discord.Colour.orange())
  channel = guild.channels[0]
  for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send(embed=embed)
        break


@client.event
async def on_message(message):
  ctx = message.channel
  if message.content.startswith('.daily'):
    try:
      parameters = {'date': message.content.split(' ')[1]}
    except:
      parameters = {}
    if message.content.startswith('.daily random'):
      year = random.randrange(1995,2022)
      month = random.randrange(1,13)
      if month in [1,3,5,7,8,10,12]:
        date = random.randrange(1,32)
      else:
        date = random.randrange(1,31)
      message = f'.daily {year}-{month}-{date}'
      await ctx.send(message)
    else:
      try:
        req = literal_eval(requests.get (f'https://api.nasa.gov/planetary/apod?api_key={api_key}', params=parameters).text)
        title = req['title']
        desc = f'''{req['date']}\nDiscover the cosmos!\n\n{req  ['explanation']}'''
        try:
          url = req['hdurl']
        except:
          url = req['url']
          name = url
        embed = discord.Embed(title=title, url=url, description=desc, color=discord.Color.orange())
        embed.set_footer(text="Each day a different image or photograph of our fascinating universe is featured, along with a brief explanation written by a professional astronomer.")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

        try:
          if name:
            name = f'https://youtube.com/watch?v={name[30:41]}'
            embed = discord.Embed(title=title, url=url,   description=desc,color=discord.Color.orange(),video =   {'url':url})
            await ctx.send(name)
        except:
          pass
      except:
        await ctx.send('Either your date is invalid or you\'ve chosen   a date too far back. Try another one, remember, it has to be  in YYYY-MM-DD format and it also must be after 1995-06-16, the   first day an APOD picture was posted')

    
  elif message.content.startswith('.help'):
    embed = discord.Embed(title='Help has arrived.', description='''As of now, there are only the following commands- \n\n`.daily`   -  See the NASA astronomy picture of the day, along with an explanation of the picture. \n    __Specific date__  - In YYYY-MM-DD format to get an image from that date! (Example - `.daily 2005-06-08`, this was for 8th June, 2005) \n    __Random APOD Photo__ - You can now request a random APOD photo from the archive using `.daily random` \n\n`.channel` - get daily apod picture automatically to the channel in which you post this message. \n\n`.remove` - remove your channel from the daily APOD picture list. \n\n `.info <query>` - The ultimate source for data, videos and pictures on ANYTHING related to space science. \n\n`.iss` - Find the live location of the international space station with respect to the Earth.\n\n`.fact` - gives a random fact from the fact library. \n\nHave fun!''', color=discord.Color.orange())
    embed.set_footer(text= "This bot has been developed with blood, tears, and loneliness.")
    await ctx.send(embed=embed)
  elif message.content.startswith('.channel'):
    db[message.guild.id] = ctx.id
    mes = await ctx.send('Registered.')
    sleep(2)
    await mes.delete()
    await message.delete()
  #just something i added to trigger the daily photo if somehow the bot doesnt do it 
  #by itself. Dont blame me if you understood the reference. eheheeheh
  elif message.content.lower().startswith('execute order 66'):
    if message.author.id == 756496844867108937:
      await ctx.send('Are you sure, senator Palpatine?')      
      def check(msg):
        if msg.content.lower().startswith('yes'):
          return True
      try:
        message = await client.wait_for('message', timeout=60.0, check=check)
      except:
        await ctx.send('Never mind.')
      else:
        await ctx.send('Yes my lord.')
        for guild in db.keys():
          try:
            channel = client.get_channel(db[guild])
            await channel.send('.daily')
          except:
            pass
  #removes a given channel from the apod service.
  elif message.content.startswith('.remove'):
    del db[str(message.guild.id)]
    mes = await ctx.send('Removed from daily APOD feed.')
    sleep(2)
    await message.delete()
    await mes.delete()
  #returns the user id
  elif message.content.startswith('.id'):
    await ctx.send(message.author.id)
  #this info command first checks the total number of pages by going to 
  #the 100th page (since no queries are 100 pages long, the image and 
  #video api just mentions the last valid page number) and 
  #takes the last page number from there, uses the random library to pick 
  #any page from the total pages, takes the description and image and 
  #then uses the solar system open data api to pick numerical data 
  #regarding the query, if it is an astronomical body. oof.
  elif message.content.startswith('.info'):
    try:
      q = str(message.content)[6:]
      req3 = literal_eval(requests.get(f'https://images-api.nasa.gov/search?q={q}&page=100').text)['collection']['links'][0]['href'][-1]
      parameters = {'page': str(random.randrange(1,int(req3)+1))}
      req2 = literal_eval(requests.get(f'https://images-api.nasa.gov/search?q={q}',params = parameters) .text)
      choice = random.choice(dict(req2['collection'])['items'])
      desc = str(choice['data'][0]['description']).capitalize()
      embed = discord.Embed(title = q.title() , description = desc.capitalize() ,   color=discord.Color.orange())
      url = (choice['links'][0]['href']).replace(' ','%20') 
      try:
        req = json.loads(requests.get(f'https://api.le-systeme-solaire.net/rest/bodies/{q}').text)

        if req['mass']:
          a = str(req['mass']['massValue'])
          b = str(req['mass']['massExponent'])
          embed.add_field(name = 'Mass' , value = f'{a} x 10^{b} kg')
        else:
          embed.add_field(name = 'Mass', value = 'Unknown')

        if not req['density']:
          embed.add_field(name='Density' , value = 'Unknown')
        else:
          embed.add_field(name='Density' , value = str(req['density'])+ ' g/cm³')

        if not req['gravity']:
          embed.add_field(name='Gravity' , value = 'Unknown')
        else:
          embed.add_field(name='Gravity' , value = str(req['gravity']) + ' m/s²')

        if not req['sideralOrbit']:
          embed.add_field(name = 'Period of Revolution', value = 'Unknown')
        else:
          embed.add_field(name = 'Period of Revolution', value = str(req['sideralOrbit']) + '  days')

        if not req['sideralRotation']:
         embed.add_field(name = 'Period of Rotation', value = 'Unknown')
        else:
          embed.add_field(name = 'Period of Rotation', value = str(req['sideralRotation']) + '   hours')

        if req['meanRadius']:
          a = req['meanRadius']
          embed.add_field(name = 'Mean Radius' , value = f'{a} km')
        else:
          embed.add_field(name = 'Mean Radius' , value = 'Unknown')

        if not req['escape']:
          embed.add_field(name = 'Escape Velocity', value = 'Unknown')
        else:
          a = req['escape']
          embed.add_field(name = 'Escape Velocity', value = f'{a} m/s') 

        if not req['discoveredBy']:
          embed.add_field(name='Discovered By' , value = 'Unknown')
        else:
          embed.add_field(name='Discovered By' , value = req['discoveredBy'])

        if not req['discoveryDate']:
          embed.add_field(name='Discovery Date' , value = 'Unknown')
        else:
          embed.add_field(name='Discovery Date' , value = req['discoveryDate'])

        if not req['moons']:
          aroundPlanet = req['aroundPlanet']['planet'].title()
          embed.add_field(name = 'Around Planet',value = aroundPlanet)
        else:
          numMoons = len(req['moons'])
          embed.add_field(name = 'Moons',value = numMoons)
        
      except:
        pass
      embed.set_image(url = url)
      text = 'Built using the Solar system OpenData Api and the NASA video and image library.'
      embed.set_footer(text = text)
      await ctx.send(embed = embed)
    except:
      await ctx.send('You have not specified a query or your query is wrong, use `.info <query>`')
  #sends APOD message if one has been released. This piece of code is triggered whenever a message in any server is sent. If it finds a new photo, it saves the updated date in db['apod'] and never does this again till the next day.
  elif message.content.startswith('.whereiss') or message.content.startswith('.iss'):
    req = literal_eval(requests.get('https://api.wheretheiss.at/v1/satellites/25544').text)
    result = reverse_geocoder.search((round(req['latitude'],3),round(req['longitude'],3)),mode = 1)[0]
    location = ''
    if result['name']:
      location += result['name'] + ', '
    if result['admin1']:
      location += result['admin1'] + ', '
    if result['admin2']:
      location += result['admin2'] + ', '
    if result['cc']:
      location += find_country(result['cc'])
    location.replace('`', '')
    lat,long = round(req['latitude'],3),round(req['longitude'],3)
    place = f'{lat},{long}'
    url = f'https://www.mapquestapi.com/staticmap/v5/map?size=700,400@2x&zoom=2&defaultMarker=marker-FF0000-FFFFFF&center={place}&type=map&locations={place}&key={api_key2}'
    embed = discord.Embed(title = 'International Space Station',description = f'The International Space Station is currrently near `{location}`.' , color = discord.Color.orange())
    embed.set_image(url=url)
    velocity = round(req['velocity'],2)
    embed.add_field(name = 'Velocity' , value = f'{velocity} km/hr') 
    altitude = round(req['altitude'],2)
    embed.add_field(name = 'Altitude' , value = f'{altitude} km')
    embed.add_field(name ='Visibility',value = req['visibility'].title())
    embed.set_footer(text='This request was built using the python reverse_geocoder library, WhereTheIssAt API and the MapQuest Api.')
    await ctx.send(embed=embed)
  elif message.content.startswith('.fact'):
    line = random_fact()
    title,desc = line[0],line[1]
    embed = discord.Embed(title = title , description = desc, color = discord.Color.orange())
    try:
      embed.set_image(url=line[2])
      embed.set_footer(text=line[3])
    except:
      pass
    await ctx.send(embed = embed)
  parameters = {'date':strftime('%Y-%m-%d')}
  if db['apod'] != strftime('%Y-%m-%d') and int(strftime('%H')) > 4 and (requests.get(f'https://api.nasa.gov/planetary/apod?api_key={api_key}',params=parameters).text)[8:11] != '404':  
      db['apod'] = strftime('%Y-%m-%d')
      for guild in db.keys():
        try:
          channel = client.get_channel(db[guild])
          await channel.send('.daily')
        except:
          pass
  
  
      





keep_alive()
client.run(os.environ['TOKEN'])

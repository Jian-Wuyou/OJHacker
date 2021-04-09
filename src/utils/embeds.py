from dataclasses import dataclass

import discord

@dataclass
class Embeds:
    author = {
        'name': 'OJ Hacker',
    }

    thumbnail = {
        'url': 'https://cdn.discordapp.com/avatars/824228153480052746'
               '/d422b4a513ea7ba71f1bb0839edc1fb0.png?size=128'
    }

    instructions: discord.Embed = discord.Embed.from_dict({
        'title': 'List of Commands:',
        'author': author,
        'thumbnail': thumbnail,
        'description': '~ use this to access its features',
        'color': 7379967,
        'type': 'rich',
        'fields': [
            {'inline': False,
            'name': '1. !insert_tc (or !it) {LE/PA/MP}{number} {label}',
            'value': '- insert a test case for a specific problem'},
            {'inline': False,
            'name': '2. !penge_tc (or !ptc) {LE/PA/MP}{number}',
            'value': '- get all testcases for a specific problem'},
            {'inline': False,
            'name': '3. !penge_random (or !pr) {LE/PA/MP}{number}',
            'value': '- get a randomly generated testcase for a specific problem'},
            {'inline': False,
            'name': '4. !tcs_nga (or !tn) {LE/PA/MP}{number}',
            'value': '- shows the list of stored testcases for a specific problem'},
            {'inline': False,
            'name': '5. !share_ko_lang (or !skl) {UID}',
            'value': '- shows the test case with given uid'},
            {'inline': False,
            'name': 'Example:',
            'value': '!insert_tc PA05 test'}
        ],
    })
    no_testcases: discord.Embed = discord.Embed.from_dict({
        'title': 'No Testcases Yet',
        'author': author,
        'thumbnail': thumbnail,
        'description': '~ with the possible following reasons:',
        'color': 7379967,
        'type': 'rich',
        'fields': [
            {'inline': False,
             'name': '1. No one has solved it yet',
             'value': 'So sad.'},
            {'inline': False,
             'name': '2. The problem does not exist.',
             'value': 'Baka na-typo ka ser!'}
        ],
    })

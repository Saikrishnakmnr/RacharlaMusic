def generate(title: str, language: str, style: str) -> str:

    title = title.strip()

    if not title:
        title = "మన పాట" if "Telugu" in language else "Our Song"

    if language == "English":

        return f"""[Verse]

Under the light we find a way
A little hope can change the day
Every heartbeat carries on
Turning the night into a dawn

[Pre-Chorus]

Hold on close, don't let it go
Let the feeling gently grow

[Chorus]

{title}, stay with me tonight
{title}, make the dark feel bright
Every dream is calling out
Sing it loud, remove the doubt

[Verse]

Step by step and side by side
Keep the fire burning inside
When the world is moving fast
Make this beautiful moment last

[Bridge]

One more breath, one more chance
Let the soul begin to dance

[Outro]

{title}
We'll carry this melody home
"""

    moods = {
        "Melody": (
            "మధురమైన రాగమై",
            "మనసంతా మురిసేలా",
        ),
        "Romantic": (
            "ప్రేమ అనే పాటగా",
            "నీతోనే సాగాలి",
        ),
        "Folk": (
            "పల్లె గాలి వీచగా",
            "మన ఊరు పాడగా",
        ),
        "Mass": (
            "దూసుకెళ్లే జోష్ ఇదే",
            "మన అడుగే జైత్రయాత్ర",
        ),
        "Sad": (
            "చీకటిలో జ్ఞాపకమై",
            "కన్నీటిలో పాటగా",
        ),
        "Cinematic": (
            "వెండి తెర కలలా",
            "వేల రంగుల వేడుకలా",
        ),
        "Lo-fi": (
            "నిశ్శబ్ద రాత్రిలో",
            "చిన్న జ్ఞాపకమై",
        ),
        "Devotional": (
            "దైవ కృప వెలుగై",
            "నీ దయే మా బలమై",
        ),
        "Hip-hop": (
            "బీట్‌తో ముందుకు",
            "మాటతో మంటగా",
        ),
        "Rock": (
            "గుండెల్లో గర్జనగా",
            "వేగంగా ముందుకు",
        ),
        "Pop": (
            "కొత్తగా మెరిసేలా",
            "హృదయం పాడేలా",
        ),
    }

    a, b = moods.get(
        style,
        moods["Melody"],
    )

    mixed_hook = ""

    if language == "Telugu + English":
        mixed_hook = """

[English Hook]

This is our moment, this is our song
Keep moving forward, keep singing along
"""

    return f"""[పల్లవి]

{title}... {a}
{b}
నా ఊపిరిలో వినిపించే స్వరమా
నా అడుగులకు దారి చూపే వెలుగువా

[చరణం 1]

ఈ క్షణమే ఒక కొత్త కథగా
ఈ బాటలో ఒక మధుర జ్ఞాపకంగా
నవ్వులన్నీ మన వెంట నడవగా
మన కలలన్నీ నిజమై నిలవగా

[ప్రీ-కోరస్]

ఏదైనా సరే మనం కలిసి
ఎదురైనా సరే ధైర్యంగా నిలిచి

[పల్లవి]

{title}... {a}
{b}
నా ఊపిరిలో వినిపించే స్వరమా
నా అడుగులకు దారి చూపే వెలుగువా

[చరణం 2]

ఆకాశమే మన హద్దు కాదుగా
ఆశలే మన గుండె మాటగా
ప్రతి ఉదయం కొత్త వెలుగై రావగా
ప్రతి అడుగు విజయంగా మారగా

[బ్రిడ్జ్]

ఒక్క స్వరం... ఒక్క మనసై
ఒక్క కల... నిజమై
ఈ పాట ఎప్పటికీ నిలవాలి
మన కథ చిరకాలం వినిపించాలి

[పల్లవి]

{title}... {a}
{b}
నా ఊపిరిలో వినిపించే స్వరమా
నా అడుగులకు దారి చూపే వెలుగువా

[ఔట్రో]

{title}...
మనసులో మిగిలే మధుర గీతమా
{mixed_hook}
"""

def generate(title: str, language: str, style: str) -> str:
    title = title.strip() or ("మన పాట" if "Telugu" in language else "Our Song")
    english = language == "English"
    mixed = language == "Telugu + English"

    if english:
        return f"""[Verse 1]
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

[Verse 2]
Step by step and side by side
Keep the fire burning inside
When the world is moving fast
Make this beautiful moment last

[Bridge]
One more breath, one more chance
Let the soul begin to dance

[Final Chorus]
{title}, stay with me tonight
We'll carry this melody home"""

    return f"""[పల్లవి]
{title}... మధురమైన రాగమై
మనసంతా మురిసేలా
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
{title}... మధురమైన రాగమై
మనసంతా మురిసేలా
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

[Final Chorus]
{title}... మనసులో మిగిలే మధుర గీతమా
{title}... ఈ క్షణమే మన కొత్త లోకమా
""" + ("\n[English Hook]\nThis is our moment, this is our song\nKeep moving forward, keep singing along\n" if mixed else "")

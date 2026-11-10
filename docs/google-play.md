# Human Override op Google Play — stappenplan

Stand 10 november 2026. Wat al klaar is in de code:
- De app richt zich op Android 16 (API 36). Dat is verplicht voor nieuwe apps sinds 31 augustus 2026.
- GitHub bouwt bij elke wijziging een **.aab**-bestand voor Google Play (artifact `human-override-google-play-aab`,
  te vinden bij **Actions → Human Override Android app → laatste run → Artifacts**).
- Er zit een link naar het privacybeleid in de app, en een sabotage-logboek.
- Zodra jouw vaste sleutel als GitHub-secret bestaat, gebruikt de build die automatisch. Ook de APK op de site
  krijgt dan altijd dezelfde handtekening, zodat mensen kunnen bijwerken zonder eerst te verwijderen.

Wat alleen jij kunt doen staat hieronder. Deel nooit een wachtwoord of sleutelbestand in een chat.

## 1. Je vaste uploadsleutel maken (één keer, ±10 minuten)
1. Installeer Java: ga naar **adoptium.net**, klik **Download Temurin**, installeer met de standaardkeuzes.
2. Open **PowerShell** (Windows-toets, typ `PowerShell`, Enter).
3. Plak dit en druk Enter (vervang niets):
   `keytool -genkeypair -v -keystore $HOME\ho-upload.jks -alias ho -keyalg RSA -keysize 3072 -validity 10000 -dname "CN=Amghar Said, O=Human Override, C=BE"`
4. Kies een sterk wachtwoord als het gevraagd wordt (twee keer). Zet het in je wachtwoordbeheerder.
5. Maak een reservekopie van het bestand `ho-upload.jks` (uit je gebruikersmap) op een USB-stick. Kwijt = ingewikkelde
   herstelprocedure bij Google.
6. Kopieer het bestand als tekst: plak in PowerShell
   `[Convert]::ToBase64String([IO.File]::ReadAllBytes("$HOME\ho-upload.jks")) | Set-Clipboard`

## 2. De sleutel in GitHub zetten (geheim, alleen jij)
1. Ga naar **github.com/sakkesakke/geopolcoins → Settings → Secrets and variables → Actions**.
2. Klik **New repository secret** en maak deze vier:
   - `HO_UPLOAD_KEYSTORE_B64` → plak (Ctrl+V) wat je in stap 1.6 kopieerde
   - `HO_UPLOAD_STORE_PASS` → je wachtwoord
   - `HO_UPLOAD_KEY_ALIAS` → `ho`
   - `HO_UPLOAD_KEY_PASS` → hetzelfde wachtwoord
3. Ga naar **Actions → Human Override Android app → Run workflow**. In het logboek staat dan
   "Signing with the permanent upload key".

## 3. Google Play-ontwikkelaarsaccount ($25, eenmalig)
1. Ga naar **play.google.com/console** en kies **persoonlijk account**.
2. Je identiteit wordt gecontroleerd (identiteitsbewijs). Dat kan enkele dagen duren.
3. Een organisatie-account hoeft de 12 testers niet, maar vraagt een D-U-N-S-nummer. Persoonlijk is eenvoudiger.

## 4. De app aanmaken
1. **Create app** → naam `Human Override: the AI kill switch`, taal Engels, **App**, **Free**.
2. **Setup → App signing**: kies **Use Google-generated key** (Google bewaart de echte sleutel; jouw sleutel is de uploadsleutel).
3. **Privacy policy**: `https://geopolcoins.xyz/privacy.html`.
4. **Data safety**: "Collects no data" en "Shares no data". Klopt: alles blijft op de telefoon.
5. **App content → VPN service**: vraag 1 "Is VPN de kernfunctie?" → **No**. Vraag 2 → **Parental control**
   (en **Device security**). Leg uit: "Local DNS filter on the device; only DNS questions go through the
   VpnService; AI domains get 'does not exist'; no traffic leaves the phone through us, nothing is collected."
   Google vraagt ook een **video van maximaal 90 seconden**: open de app, tik op de grote knop, toon dat chatgpt.com
   niet meer opent. Opnemen met de schermopname van je telefoon, uploaden als **niet-openbare** YouTube-video.
6. **Content rating**: vul de vragenlijst in (geen geweld, geen chat, geen aankopen).
7. **Target audience**: 18+ (ouders, scholen, bedrijven). Niet "kinderen" kiezen: dat activeert extra regels.

## 5. Gesloten test met 12 testers, 14 dagen
1. **Testing → Closed testing → Create track**, upload de .aab uit GitHub.
2. Voeg minstens **15** Gmail-adressen toe (een paar reserve: wie afhaakt telt niet).
3. Deel de testlink. Testers klikken op **Become a tester** en installeren via Play.
4. Ze moeten **14 dagen achter elkaar** ingeschreven blijven. Daarna: **Apply for production**.
5. Google beoordeelt dat meestal binnen 7 dagen. Reken in totaal op ongeveer 3 weken.

## Teksten voor de winkel
- Korte beschrijving (max. 80 tekens):
  EN `Block AI chatbots in every app. PIN lock, tamper log. Free, no account.`
  NL `Blokkeer AI-chatbots in elke app. Pincode, sabotage-logboek. Gratis.`
  FR `Bloquez les chatbots IA dans toutes les applis. PIN, journal. Gratuit.`
- Lange beschrijving: neem de tekst over uit `docs/store-kit/README.md` en vervang "browser" door "phone". Voeg toe:
  "Uses Android's VpnService only as a local DNS filter: only address lookups pass through the app, AI addresses get
  'does not exist', all other traffic goes straight to the internet. Nothing is collected or sent to us."
- Schermafbeeldingen: maak 2 tot 4 schermafdrukken op je telefoon (grote knop aan, logboek, sensorcheck).

Prijzen of abonnementen: pas na de beslissing over de prijs (herinnering 14 november). Dit is geen juridisch advies.

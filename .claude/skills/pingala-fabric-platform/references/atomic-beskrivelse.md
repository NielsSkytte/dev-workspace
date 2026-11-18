# Pingala Atomic: beskrivelse

> Status 2026-11-16. Hvad Atomic er, og hvad det løser. Teknisk detalje står i `atomic-overview.md`
> og `atomic.md`.

## 1. Grundprincip

Atomic er Pingalas accelerator til en dataplatform på Microsoft Fabric med ERP-data som kilde. Den
består af færdige, testede byggeklodser, der fører data fra kildesystemet til en datamodel, som
rapporter og analyser læser fra.

Tre principper bærer hele designet:

1. **Samme indlæsning for alle data.** Alle tabeller hentes, holdes opdateret og gemmes med
   historik på samme måde. Der bygges ikke noget særskilt pr. tabel.
2. **Forretningsreglerne ligger ét sted.** Hver regel er beskrevet ét sted og kan læses og
   ændres der.
3. **Nyt indhold kræver ingen ombygning.** En ny tabel eller et nyt begreb tilføjes, uden at
   platformens maskinrum skal ændres.

Navnet kommer fra lagene: Particles (rå historik), Atoms (forretningsentiteter), Molecules
(stjerneskemaet) og Measures (den semantiske model).

## 2. Problemet i et F&O-setup

| Uden Atomic | Med Atomic |
|---|---|
| 60-80 % af projekttiden går med at bygge fundamentet, før noget kan testes | Fundamentet findes og er testet; projektet starter på forretningsindholdet |
| Hver F&O-tabel skal have sin egen indlæsning | Alle tabeller hentes på samme måde |
| Udtræk via F&O-entiteter kræver en D365-udvikler | Data hentes direkte fra F&O-tabellerne; F&O skal ikke ændres |
| F&O viser kun, hvordan data ser ud nu | Fuld historik: man kan se, hvordan data så ud på en given dato |
| F&O gemmer mange værdier som koder | Koderne vises som læsbar tekst |
| Forretningsreglerne spredes ud over mange steder | Hver regel ligger ét sted |
| Hvert projekt bygges på sin egen måde | Samme opbygning og navngivning på alle projekter |
| Det er besværligt og fejlbehæftet at flytte løsningen fra udvikling til test og drift | Løsningen flyttes uændret mellem miljøerne |

**Ikke kun F&O.** Atomic er designet til D365 F&O og kører også på Dynamics AX 2009. Mønsteret er
ikke bundet til ét ERP: en kilde, hvis data har en nøgle, går gennem de samme lag. Kun vejen ind i
Fabric er kildespecifik. Det bruges i dag med CRM/Dataverse, REST-API'er, marketingplatforme,
webanalyse og regneark. ServiceNow og SAP er under udvikling som kilder. Kilderne mødes i ét
fælles stjerneskema, så ERP, CRM og service kan analyseres sammen.

## 3. Lagene

Data bevæger sig gennem fem lag. Hvert lag har én opgave.

| Lag | Hvad det løser |
|---|---|
| **Landing Zone** | Kildens data ankommer urørt, så kilden aldrig belastes af transformationer, og alt kan genindlæses. |
| **Raw (Particles)** | Fuld historik på alle tabeller. Man kan altid se, hvordan data så ud på en given dato, også når kilden kun kender nu. |
| **Enriched (Atoms)** | Kildens tekniske tabeller bliver til forretningsbegreber: kunde, ordre, vare, postering. Pr. kilde. |
| **Curated (Molecules)** | Ét fælles stjerneskema på tværs af kilder: dimensioner og fakta, klar til rapportering. Her ligger også data, der skal sendes tilbage til andre systemer. |
| **Semantisk model (Measures)** | Ét sted for nøgletal, beregninger og adgangsstyring, så alle rapporter regner ens. |

Ved siden af lagene sørger et fælles hjælpelag for kalender, læsbare tekster til koder og styring
af indlæsningen. Én master-pipeline kører det hele i rækkefølge.

## 4. Atomic i Microsoft-økosystemet

| Område | Hvad Atomic giver |
|---|---|
| **Dataverse ind** | F&O- og CRM-data hentes med Microsofts egen Link to Fabric. Ingen egen integration at vedligeholde. |
| **Dataverse ud** | Renset og samlet data kan skrives tilbage til Dataverse, fx kunder og kontakter til en Sales- eller Service-app. Platformen bliver kilde, ikke kun modtager. |
| **Power Platform** | Power Apps, Power Automate og Copilot Studio arbejder på Dataverse og får dermed adgang til de samme data som rapporterne. |
| **Power BI** | Én semantisk model over stjerneskemaet, opdateret automatisk efter hver kørsel. Samme nøgletal i alle rapporter og adgang styret ét sted. |
| **AI og data agents** | Faste navne og en dokumenteret model gør, at Fabric data agents kan svare på spørgsmål om data. |
| **Andre systemer** | Samme udgående mønster leverer data til fx marketing- og partnersystemer. |
| **Miljøer** | Alt ligger som kode og flyttes uændret mellem DEV, TEST og PROD. |

## 5. Tilknyttet produkt: MetaAtomic

MetaAtomic køres oven på en Atomic-platform: sporbarhed fra rapport til kildekolonne, modenhed pr.
datastrøm og miljø, datakvalitetsregler og en portal. Det virker, fordi Atomics konventioner er
faste.

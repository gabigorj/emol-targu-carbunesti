# Sincronizare gratuită eMOL – dispozițiile autorității executive

Sursă: https://emol.ro/targucarbunesti-gj/registru-dp/

Workflow-ul rulează la fiecare 6 ore și manual, în GitHub Actions. Folosește Playwright, fără TinyFish sau API plătit. Publică doar rândurile din registrul public care au număr, dată, titlu și link individual valid. Dacă eMOL schimbă structura paginii, execuția eșuează fără a suprascrie datele existente. Selectorii necesită verificare la prima rulare pe GitHub, fiindcă sursa nu a putut fi testată din mediul local.

## Activare
1. În Settings > Actions > General setează Workflow permissions la Read and write permissions dacă este necesar.
2. În Actions rulează manual Sincronizare dispozitii eMOL și verifică jurnalul și data/dispozitii.json.
3. Wix citește https://raw.githubusercontent.com/gabigorj/emol-targu-carbunesti/main/data/dispozitii.json

Nu se publică dispoziții individuale cu caracter personal care nu sunt expuse public de eMOL. Lista este un instantaneu actualizat periodic, nu flux în timp real.

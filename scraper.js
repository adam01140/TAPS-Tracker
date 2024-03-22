const puppeteer = require('puppeteer');
const admin = require('firebase-admin');
const serviceAccount = require('./defundtaps-firebase-adminsdk-l7ji6-497e092431.json');

admin.initializeApp({
    credential: admin.credential.cert(serviceAccount),
});

const db = admin.firestore();

async function scrapeCitation(citationNumber) {
    const browser = await puppeteer.launch({ headless: "new" });
    const page = await browser.newPage();

    const url = `https://www.paymycite.com/SearchAgency.aspx?agency=147&plate=&cite=${citationNumber}`;
    await page.goto(url, { waitUntil: 'domcontentloaded' });

    const button = await page.$('#DataGrid1_ctl02_cmdContest');

    if (!button) {
        console.error(`[${citationNumber}] does not have a button`);
        await browser.close();
        return;
    }

    try {
        await Promise.all([
            button.click(),
            page.waitForNavigation({ timeout: 5000 })
        ]);
    } catch (e) {
        if (e instanceof puppeteer.errors.TimeoutError) {
            console.error(`[${citationNumber}] Navigation timeout after clicking the button. Moving to the next citation.`);
            await browser.close();
            return;
        }
        throw e;
    }

    const [dateElement, timeElement, dayElement, locationElement, citeNumberElement] = await Promise.all([
        page.$('#txtCiteDate'),
        page.$('#txtCiteTime'),
        page.$('#txtDayOftheWeek'),
        page.$('#txtVioLocation'),
        page.$('#txtCiteNumber')
    ]);

    if (!dateElement || !timeElement || !dayElement || !locationElement || !citeNumberElement) {
        console.error(`Unable to fetch data for citation #${citationNumber}`);
        await browser.close();
        return;
    }

    const date = await dateElement.evaluate(el => el.textContent);
    const time = await timeElement.evaluate(el => el.textContent);
    const day = await dayElement.evaluate(el => el.textContent);
    const location = await locationElement.evaluate(el => el.textContent);
    const citeNumber = await citeNumberElement.evaluate(el => el.textContent);

    await db.collection('citations').doc(`${citationNumber}`).set({
        timestamp: date,
        time: time,
        citationDay: day,
        college: location,
        citationNumber: citeNumber
    });

    await browser.close();
    console.log(`Stored citation #${citationNumber}`);
}

async function startScraping(startingCitation, endingCitation) {
    for (let currentCitation = startingCitation; currentCitation <= endingCitation; currentCitation++) {
        await scrapeCitation(currentCitation);
    }
    console.log('Scraping process completed.');
}

startScraping(366123456, 400127499);

const express = require('express');
const puppeteer = require('puppeteer');
const mongoose = require('mongoose');

const app = express();
const PORT = 3000;

mongoose.connect('mongodb://localhost:27017/citationsDB', { useNewUrlParser: true, useUnifiedTopology: true });
const Citation = mongoose.model('Citation', {
    college: String,
    timestamp: String,
    time: String,
    citationNumber: Number,
    citationDay: String
});

app.get('/api/citations', async (req, res) => {
    const citations = await Citation.find().sort({ citationNumber: -1 }).limit(100);
    res.json(citations);
});

async function scrapeCitation(citationNumber) {
    const initialURL = `https://www.paymycite.com/SearchAgency.aspx?agency=147&plate=&cite=${citationNumber}`;
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();
    await page.goto(initialURL, { waitUntil: 'networkidle2', timeout: 30000 });
    const contestButton = await page.$("#DataGrid1_ctl02_cmdContest");
    if (!contestButton) {
        await browser.close();
        return;
    }
    await contestButton.click();
    await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 10000 });
    const location = await page.$eval('#txtVioLocation', el => el.innerText);
    const date = await page.$eval('#txtCiteDate', el => el.innerText);
    const time = await page.$eval('#txtCiteTime', el => el.innerText);
    const citationDay = await page.$eval('#txtDayOftheWeek', el => el.innerText);
    if (location && date && time) {
        const newCitation = new Citation({
            college: location,
            timestamp: date,
            time: time,
            citationNumber: citationNumber,
            citationDay: citationDay
        });
        await newCitation.save();
    }
    await browser.close();
}

async function startScraping(startingCitation, endingCitation) {
    for (let currentCitation = startingCitation; currentCitation <= endingCitation; currentCitation++) {
        await scrapeCitation(currentCitation);
    }
}

startScraping(400126027, 400127000);

app.listen(PORT, () => {
    console.log(`Server started on http://localhost:${PORT}`);
});

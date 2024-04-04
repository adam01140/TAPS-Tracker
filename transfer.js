const admin = require('firebase-admin');

// Initialize Firebase Admin SDK
const serviceAccount = require('./transfer.json');

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});

const db = admin.firestore();

// Heroku endpoint to post citations
const HEROKU_URL = 'https://thawing-bayou-15449-25148cb91854.herokuapp.com/api/citations';

async function transferData() {
  // Dynamically import node-fetch
  const fetch = (await import('node-fetch')).default;

  // Fetch citations from Firebase
  const snapshot = await db.collection('citations').get();

  snapshot.forEach(async (doc) => {
    const citationData = doc.data();
    
    // Combine date and time from Firebase into a single datetime string in ISO format
    // Assume time is in HHMM format and timestamp is in MM/DD/YYYY format
    const dateTimeISO = `${citationData.timestamp.split('/').reverse().join('-')}T${citationData.time.slice(0, 2)}:${citationData.time.slice(2, 4)}:00Z`;

    const postData = {
      citationNumber: citationData.citationNumber || 'Unavailable',
      timeOccurred: dateTimeISO,
      locationOccurred: citationData.college || 'Unavailable',
      licensePlate: citationData.licensePlate || 'Unavailable',
      // Add other fields as necessary
    };

    try {
      const response = await fetch(HEROKU_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(postData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const responseData = await response.json();
      console.log('Successfully transferred citation data:', responseData);
    } catch (error) {
      console.error('Error transferring citation data:', error);
    }
  });
}

transferData();

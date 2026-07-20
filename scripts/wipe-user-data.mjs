// One-off: fully wipes a single user's Firestore data (folders, folder
// items, and the users/{uid} doc itself, including usageCount and any
// Stripe fields) so they can go through a completely clean test. Mirrors
// the deletion order in the iOS repo's FirebaseManager.deleteAccount():
// items -> folders -> user doc. Does NOT delete the Firebase Auth account;
// that has to be done separately (Firebase Console, or grant the service
// account Firebase Authentication Admin to do it programmatically).
//
// Usage: netlify dev:exec -- node scripts/wipe-user-data.mjs <uid>
import { listCollectionAdmin, deleteDocAdmin } from '../Netlify/Functions/lib/firestoreAdmin.js';

const uid = process.argv[2];
if (!uid) {
  console.error('Usage: node scripts/wipe-user-data.mjs <uid>');
  process.exit(1);
}

const folderIds = await listCollectionAdmin(`users/${uid}/folders`);
for (const folderId of folderIds) {
  const itemIds = await listCollectionAdmin(`users/${uid}/folders/${folderId}/items`);
  for (const itemId of itemIds) {
    await deleteDocAdmin(`users/${uid}/folders/${folderId}/items/${itemId}`);
    console.log(`Deleted item ${itemId} in folder ${folderId}`);
  }
  await deleteDocAdmin(`users/${uid}/folders/${folderId}`);
  console.log(`Deleted folder ${folderId}`);
}

await deleteDocAdmin(`users/${uid}`);
console.log(`Deleted users/${uid}`);
console.log('Done. Firestore data fully wiped. Firebase Auth account still exists.');

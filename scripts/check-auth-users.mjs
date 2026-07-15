// One-off diagnostic: confirms whether given Firebase UIDs are real signed-up
// accounts (email/password or Google) or anonymous guest sessions, so the
// grandfathering migration only targets real people.
async function getAccessToken() {
  const serviceAccount = JSON.parse(process.env.GCP_SERVICE_ACCOUNT_KEY);
  const { SignJWT, importPKCS8 } = await import('jose');
  const privateKey = await importPKCS8(serviceAccount.private_key, 'RS256');
  const now = Math.floor(Date.now() / 1000);
  const assertion = await new SignJWT({ scope: 'https://www.googleapis.com/auth/identitytoolkit' })
    .setProtectedHeader({ alg: 'RS256' })
    .setIssuer(serviceAccount.client_email)
    .setAudience('https://oauth2.googleapis.com/token')
    .setIssuedAt(now)
    .setExpirationTime(now + 3600)
    .sign(privateKey);
  const res = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ grant_type: 'urn:ietf:params:oauth:grant-type:jwt-bearer', assertion }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(JSON.stringify(data));
  return data.access_token;
}

const uids = process.argv.slice(2);
const accessToken = await getAccessToken();
const res = await fetch(`https://identitytoolkit.googleapis.com/v1/projects/tutor-mate-476113/accounts:lookup`, {
  method: 'POST',
  headers: { Authorization: `Bearer ${accessToken}`, 'Content-Type': 'application/json' },
  body: JSON.stringify({ localId: uids }),
});
const data = await res.json();
if (!res.ok) {
  console.log('FAILED:', res.status, JSON.stringify(data));
} else {
  for (const u of data.users || []) {
    const isAnonymous = !u.email && (!u.providerUserInfo || u.providerUserInfo.length === 0);
    console.log(u.localId, '| email:', u.email || '(none)', '| anonymous:', isAnonymous, '| createdAt:', new Date(Number(u.createdAt)).toISOString());
  }
}

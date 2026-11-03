/* Public client configuration only. NEVER put provider secrets or service-role keys here.
   Use one authentication project for both the website and mobile app identities.
   Leave empty to keep the prototype disconnected. */
window.AF_AUTH_CONFIG = window.AF_AUTH_CONFIG || {
  url: '',
  publishableKey: '',
  enabledProviders: [], // 'google', 'apple', 'facebook', 'linkedin_oidc'
  redirectUrl: '', // exact account page URL registered in the auth redirect allowlist
  allowSignup: false
};

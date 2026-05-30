/* Bengali language toggle — key UI strings */
const BN = {
  'Browse': 'মার্কেট',
  'Wall': 'ওয়াল',
  '🐦 Wall': '🐦 ওয়াল',
  'Pedigree': 'বংশ পরিচয়',
  'Feed Guide': 'খাদ্য গাইড',
  'Login': 'লগ ইন',
  'Join Free': 'বিনামূল্যে যোগ দিন',
  'Logout': 'লগ আউট',
  'Dashboard': 'ড্যাশবোর্ড',
  'My Pigeons': 'আমার কবুতর',
  'Messages': 'বার্তা',
  'My Offers': 'আমার অফার',
  'My Profile': 'আমার প্রোফাইল',
  '+ List Pigeon': '+ কবুতর যুক্ত করুন',
  'Find Your Perfect Pigeon': 'আপনার পছন্দের কবুতর খুঁজুন',
  'Buy & Sell Premium Pigeons': 'প্রিমিয়াম কবুতর কিনুন ও বিক্রি করুন',
  'Browse All': 'সব দেখুন',
  'Browse Pigeons →': 'কবুতর দেখুন →',
  '🐦 Start Selling Free': '🐦 বিনামূল্যে বিক্রি শুরু করুন',
  '🐦 List a Pigeon': '🐦 কবুতর যুক্ত করুন',
  'Active Listings': 'সক্রিয় বিজ্ঞাপন',
  'Pigeon Breeds': 'কবুতরের প্রজাতি',
  'Registered Sellers': 'নিবন্ধিত বিক্রেতা',
  'Commission Fee': 'কমিশন ফি',
  '🌟 Featured Pigeons': '🌟 বিশেষ কবুতর',
  'View all listings →': 'সব দেখুন →',
  'How It Works': 'কীভাবে কাজ করে',
  'Create Account': 'অ্যাকাউন্ট তৈরি করুন',
  'List Your Pigeon': 'কবুতর তালিকাভুক্ত করুন',
  'Connect & Earn': 'সংযুক্ত হন ও আয় করুন',
  'Get Started Free': 'বিনামূল্যে শুরু করুন',
  'Create Free Account': 'বিনামূল্যে অ্যাকাউন্ট তৈরি করুন',
  'Browse Listings First': 'আগে বিজ্ঞাপন দেখুন',
  'Ready to Sell Your Pigeons?': 'কবুতর বিক্রি করতে প্রস্তুত?',
  'Ready to List a New Pigeon?': 'নতুন কবুতর যুক্ত করতে প্রস্তুত?',
  '🐦 Community Wall': '🐦 কমিউনিটি ওয়াল',
  'See all posts →': 'সব পোস্ট দেখুন →',
  'Notifications': 'বিজ্ঞপ্তি',
  '🔔 Notifications': '🔔 বিজ্ঞপ্তি',
  'Mark all read': 'সব পঠিত করুন',
  'Follow': 'অনুসরণ করুন',
  'Following': 'অনুসরণ করছেন',
  'Followers': 'অনুসারী',
  '+ Follow': '+ অনুসরণ করুন',
  '✓ Following': '✓ অনুসরণ করছেন',
  'Search pigeons...': 'কবুতর খুঁজুন...',
  'Search': 'অনুসন্ধান',
  'Price is negotiable': 'দাম আলোচনাসাপেক্ষ',
  'Publish Listing': 'বিজ্ঞাপন প্রকাশ করুন',
  'Cancel': 'বাতিল',
  'Post': 'পোস্ট',
  'Like': 'পছন্দ',
  'Comment': 'মন্তব্য',
  'Share': 'শেয়ার',
  'Send': 'পাঠান',
  'Make an Offer': 'অফার করুন',
  'Send Offer': 'অফার পাঠান',
  '📅 Pigeon Events': '📅 কবুতর ইভেন্ট',
  '🏆 Pigeon Photo Contests': '🏆 কবুতর ফটো প্রতিযোগিতা',
  '📊 Market Insights': '📊 বাজার বিশ্লেষণ',
  'FOR SALE': 'বিক্রয়ের জন্য',
  'View all →': 'সব দেখুন →',
};

const EN = Object.fromEntries(Object.entries(BN).map(([k,v]) => [v,k]));
let currentLang = localStorage.getItem('bph_lang') || 'en';

function applyLang(lang) {
  const dict = lang === 'bn' ? BN : EN;
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (dict[key]) el.textContent = dict[key];
  });
  // Also walk text nodes (simpler elements)
  document.querySelectorAll('a, button, h1, h2, h3, label, .btn-primary, .btn-outline, .section-title, .hiw-title, .hw-title').forEach(el => {
    const text = el.textContent?.trim();
    if (text && dict[text]) el.textContent = dict[text];
  });
  const btn = document.getElementById('lang-btn');
  if (btn) btn.textContent = lang === 'bn' ? 'EN' : 'বাং';
  document.documentElement.lang = lang === 'bn' ? 'bn' : 'en';
}

function toggleLang() {
  currentLang = currentLang === 'en' ? 'bn' : 'en';
  localStorage.setItem('bph_lang', currentLang);
  applyLang(currentLang);
}

// Apply on load
document.addEventListener('DOMContentLoaded', () => {
  if (currentLang === 'bn') applyLang('bn');
  const btn = document.getElementById('lang-btn');
  if (btn) btn.textContent = currentLang === 'bn' ? 'EN' : 'বাং';
});

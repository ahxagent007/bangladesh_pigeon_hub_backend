# BD Pigeon Hub — Flutter App

Flutter mobile client for the Bangladesh Pigeon Hub platform. Consumes the Django REST API (`/api/`) with JWT authentication.

> **Last synced with backend:** 2026-06-06
> **Backend Python:** 3.9 · **Django:** 6.0.3 · **DRF:** 3.17.0 · **SimpleJWT:** 5.5.1
> **Flutter project location:** `F:\AlphaCue Technologies\BPH\BHP_Flutter\` (sibling of this repo)
> **Build status:** Phases 1–4 complete & compiling (`flutter build apk --debug` passes). Phases 5–11 pending.

> ⚠️ **Architecture note — the actual build diverged from the original plan below.**
> A dependency conflict between `riverpod_generator` and `hive_generator` against the Dart 3.11 SDK forced dropping all code generation during Phase 1. The shipped app therefore uses:
> - **Manual Riverpod providers** (`StateNotifier` / `FutureProvider` / `StateProvider`) — *not* `riverpod_annotation` codegen
> - **Hand-written `fromJson`** on plain classes (with `equatable` where needed) — *not* `freezed` / `json_serializable`
> - **`AppConfig` Dart enum** (`Env.dev` / `Env.prod`) for base URLs — *not* `flutter_dotenv`
> - **`hooks_riverpod`** (+ `flutter_hooks`) instead of bare `flutter_riverpod`
>
> The "Tech Stack", "Dependencies", and "Development Phases" sections below have been updated to match the real build. The earlier model/state snippets (freezed/riverpod_annotation style) are kept as **reference shapes only** — translate them to manual classes when implementing.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [Environment Setup](#environment-setup)
- [Architecture](#architecture)
- [Screens & Navigation](#screens--navigation)
- [API Integration](#api-integration)
- [Data Models](#data-models)
- [State Management](#state-management)
- [Development Phases](#development-phases)
- [Running the App](#running-the-app)
- [Backend Coordination Notes](#backend-coordination-notes)

---

## Features

Status legend: ✅ built · 🟡 partial · ⬜ not started · 🚧 blocked on backend API

| Module | Features | Status |
|---|---|---|
| **Auth** | Register, login, logout, JWT token refresh, profile edit | ✅ (login/register/refresh/forgot) · ⬜ profile edit |
| **Home** | Hero search, live-auction strip with countdown, featured listings grid, wall preview, guest CTA, pull-to-refresh, notif bell badge | ✅ |
| **Marketplace** | Browse listings, filter by breed/price/district/search, listing detail, save/unsave, make offer | ✅ browse/filter/detail/save/offer · ⬜ create listing |
| **Offers & Payments** | View sent/received offers, accept/reject/counter, submit bKash/Nagad/Rocket payment with TXN ID | ✅ |
| **My Pigeons** | List, add, edit, delete pigeons; image upload; pigeon detail; image edit-authenticity score badge | ✅ |
| **Auctions** | Live auction list, auction detail with real-time countdown, place bid, anti-snipe extension, poll endpoint for live updates | ⬜ |
| **Wall** | Social feed — create posts with images & pigeon tag, like/unlike, comment, image authenticity badge | ⬜ |
| **Notifications** | In-app notification list, unread count badge, mark-all-read on open | 🟡 (count badge live on Home; full screen ⬜) |
| **Pedigrees** | View multi-generation family tree (sire/dam), edit pedigree links | ⬜ (API ready: `/api/pedigree/<id>/` + `/edit/`) |
| **Feed Generator** | Select purpose + optional protein target → grain mix with nutritional breakdown | ⬜ (API ready: `/api/feed/generate/`) |
| **Messaging** | Inbox, 1-to-1 conversation view, send messages | ⬜ (API ready: list/detail/send · 🚧 start-conversation web-only) |
| **Dashboard / Profile** | Pigeon count, active listing count, unread message count, recent conversations, public profiles, follow | ⬜ |
| **Image Authenticity** | Show `edit_score`/`edit_label` badge on pigeon & wall images (backend EXIF analysis) | 🟡 (`EditScoreBadge` built & live on pigeon images; wall pending in Phase 7) |

---

## Tech Stack (as actually built)

| Layer | Technology |
|---|---|
| Framework | Flutter 3.41.9 (Dart 3.11.5) |
| State Management | Riverpod — `hooks_riverpod` + `flutter_hooks`, **manual** `StateNotifier`/`FutureProvider`/`StateProvider` (no codegen) |
| Navigation | `go_router` ^15.1.3 with `ShellRoute` + `_AuthListenable` refresh bridge |
| HTTP Client | `dio` ^5.9.2 (+ `pretty_dio_logger` in dev) |
| Token Storage | `flutter_secure_storage` (encrypted; access + refresh + user info) |
| Image Caching | `cached_network_image` |
| Image Picking | `image_picker` |
| Models | **Hand-written** classes with manual `fromJson` (+ `equatable`) — no freezed/json_serializable |
| Date/Time | `intl`, `timeago` |
| Countdown Timer | `dart:async` `Timer.periodic` |
| Environment | `AppConfig` Dart enum (`Env.dev`/`Env.prod`) in `lib/core/config/app_config.dart` — no dotenv |
| Misc | `shimmer` (skeletons), `badges`, `flutter_rating_bar`, `share_plus`, `url_launcher`, `connectivity_plus`, `photo_view` |

> Code generation (`build_runner`, `freezed`, `json_serializable`, `riverpod_generator`) was **removed** — do not reintroduce without resolving the `hive_generator` ↔ `riverpod_generator` analyzer conflict first.

---

## Project Structure

```
lib/
├── main.dart
├── app.dart                          # MaterialApp + GoRouter setup
├── core/
│   ├── constants/
│   │   ├── api_constants.dart        # Base URL, all endpoint paths
│   │   └── app_constants.dart        # Colors, text styles, sizes
│   ├── network/
│   │   ├── dio_client.dart           # Dio instance + interceptors
│   │   └── api_exception.dart        # Error model
│   ├── storage/
│   │   └── secure_storage.dart       # JWT token read/write/clear
│   ├── router/
│   │   └── app_router.dart           # GoRouter routes & guards
│   └── widgets/
│       ├── loading_indicator.dart
│       ├── error_view.dart
│       ├── pigeon_card.dart
│       ├── listing_card.dart
│       ├── auction_card.dart
│       ├── post_card.dart
│       └── edit_score_badge.dart     # Image authenticity badge widget
├── features/
│   ├── auth/
│   │   ├── data/
│   │   │   ├── auth_repository.dart
│   │   │   └── models/
│   │   │       └── user.dart
│   │   ├── providers/
│   │   │   └── auth_provider.dart
│   │   └── screens/
│   │       ├── splash_screen.dart
│   │       ├── login_screen.dart
│   │       ├── register_screen.dart
│   │       └── profile_edit_screen.dart
│   ├── dashboard/
│   │   ├── data/dashboard_repository.dart
│   │   ├── providers/dashboard_provider.dart
│   │   └── screens/dashboard_screen.dart
│   ├── pigeons/
│   │   ├── data/
│   │   │   ├── pigeon_repository.dart
│   │   │   └── models/
│   │   │       ├── pigeon.dart
│   │   │       ├── breed.dart
│   │   │       └── pigeon_image.dart  # now includes edit_score, edit_notes, edit_label
│   │   ├── providers/pigeon_provider.dart
│   │   └── screens/
│   │       ├── pigeon_list_screen.dart
│   │       ├── pigeon_detail_screen.dart
│   │       └── pigeon_form_screen.dart
│   ├── marketplace/
│   │   ├── data/
│   │   │   ├── marketplace_repository.dart
│   │   │   └── models/
│   │   │       ├── listing.dart        # now includes district, district_label, seller_avatar, is_saved
│   │   │       ├── offer.dart
│   │   │       └── payment.dart
│   │   ├── providers/marketplace_provider.dart
│   │   └── screens/
│   │       ├── listing_list_screen.dart
│   │       ├── listing_detail_screen.dart
│   │       ├── add_listing_screen.dart
│   │       ├── my_listings_screen.dart
│   │       ├── saved_listings_screen.dart
│   │       └── offers_screen.dart      # sent + received offers, respond, pay
│   ├── auctions/
│   │   ├── data/
│   │   │   ├── auction_repository.dart
│   │   │   └── models/
│   │   │       ├── auction.dart
│   │   │       ├── bid.dart
│   │   │       └── auction_image.dart
│   │   ├── providers/auction_provider.dart
│   │   └── screens/
│   │       ├── auction_list_screen.dart
│   │       └── auction_detail_screen.dart  # live timer + bid form + poll
│   ├── wall/
│   │   ├── data/
│   │   │   ├── wall_repository.dart
│   │   │   └── models/
│   │   │       ├── post.dart
│   │   │       ├── post_image.dart     # includes edit_score, edit_notes, edit_label
│   │   │       └── comment.dart
│   │   ├── providers/wall_provider.dart
│   │   └── screens/
│   │       ├── wall_feed_screen.dart
│   │       └── create_post_screen.dart
│   ├── notifications/
│   │   ├── data/
│   │   │   ├── notification_repository.dart
│   │   │   └── models/
│   │   │       └── notification.dart
│   │   ├── providers/notification_provider.dart
│   │   └── screens/
│   │       └── notifications_screen.dart
│   ├── pedigrees/
│   │   ├── data/
│   │   │   ├── pedigree_repository.dart
│   │   │   └── models/pedigree_record.dart
│   │   ├── providers/pedigree_provider.dart
│   │   └── screens/
│   │       ├── pedigree_tree_screen.dart
│   │       └── pedigree_edit_screen.dart
│   ├── feed_generator/
│   │   ├── data/
│   │   │   ├── feed_repository.dart
│   │   │   └── models/feed_result.dart
│   │   ├── providers/feed_provider.dart
│   │   └── screens/feed_generator_screen.dart
│   └── messaging/
│       ├── data/
│       │   ├── messaging_repository.dart
│       │   └── models/
│       │       ├── conversation.dart
│       │       └── message.dart
│       ├── providers/messaging_provider.dart
│       └── screens/
│           ├── inbox_screen.dart
│           └── conversation_screen.dart
└── shared/
    └── main_shell.dart               # Bottom navigation shell
```

---

## Dependencies (actual `pubspec.yaml`)

```yaml
dependencies:
  flutter:
    sdk: flutter
  cupertino_icons: ^1.0.8

  # State management (manual providers — no codegen)
  flutter_riverpod: ^2.6.1
  hooks_riverpod: ^2.6.1
  flutter_hooks: ^0.21.2

  # Navigation
  go_router: ^15.1.2

  # Networking
  dio: ^5.8.0
  pretty_dio_logger: ^1.4.0

  # Storage
  flutter_secure_storage: ^9.2.4
  hive_flutter: ^1.1.0          # cache (reserved for offline phase; not yet used)

  # Images
  cached_network_image: ^3.4.1
  image_picker: ^1.1.2
  photo_view: ^0.15.0

  # UI
  shimmer: ^3.0.0
  badges: ^3.1.2
  flutter_rating_bar: ^4.0.1
  intl: ^0.20.2
  timeago: ^3.7.0
  share_plus: ^11.0.0
  url_launcher: ^6.3.1
  connectivity_plus: ^6.1.4

  # Utilities
  equatable: ^2.0.7

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^6.0.0
```

> ❌ Removed from the original plan (caused SDK/analyzer resolution failure): `riverpod_annotation`, `freezed`, `freezed_annotation`, `json_serializable`, `json_annotation`, `build_runner`, `riverpod_generator`, `hive_generator`, `custom_lint`, `riverpod_lint`, `flutter_dotenv`.

---

## Environment Setup

No `.env` file. The base URL is selected by a compile-time enum in `lib/core/config/app_config.dart`:

```dart
enum Env { dev, prod }

class AppConfig {
  static const Env environment = Env.prod;   // flip to Env.dev for local backend

  static const _devBase  = 'http://127.0.0.1:8000/api';
  static const _prodBase = 'https://bdpigeonhub.com/api';
  static const _devMedia  = 'http://127.0.0.1:8000';
  static const _prodMedia = 'https://bdpigeonhub.com';

  static String get baseUrl  => environment == Env.dev ? _devBase  : _prodBase;
  static String get mediaBase => environment == Env.dev ? _devMedia : _prodMedia;
}
```

To target a local backend, set `environment = Env.dev` and adjust `_devBase`:

| Device | `_devBase` value |
|---|---|
| Android Emulator | `http://10.0.2.2:8000/api` |
| iOS Simulator | `http://localhost:8000/api` |
| Physical device (USB/LAN) | `http://<LAN-IP>:8000/api` |
| Production | `https://bdpigeonhub.com/api` (default) |

`mediaUrl(path)` in `lib/core/utils/media_url.dart` prefixes relative media paths with `mediaBase`.

---

## Architecture

```
Screen → Provider (AsyncNotifier) → Repository → DioClient → API
                                  ↑
                              SecureStorage (tokens)
```

- **Screens** are pure UI — they watch providers.
- **Providers** (`AsyncNotifier` / `FutureProvider`) hold state and call repositories.
- **Repositories** contain all API call logic and return typed model objects.
- **DioClient** — singleton Dio with two interceptors:
  1. **Auth Interceptor** — attaches `Authorization: Bearer <token>` to every request.
  2. **Refresh Interceptor** — on 401, silently calls `/api/auth/refresh/`, saves new access token, retries. If refresh fails → clear storage → navigate to `/login`.

---

## Screens & Navigation

### Route Map (`go_router`)

```
/splash                         → SplashScreen

/login                          → LoginScreen
/register                       → RegisterScreen

/ (ShellRoute — Bottom Nav)
  /home                         → ListingListScreen   (Marketplace tab)
    /home/:id                   → ListingDetailScreen
    /home/add                   → AddListingScreen
  /auctions                     → AuctionListScreen   (Auctions tab)
    /auctions/:id               → AuctionDetailScreen (live timer + bidding)
  /wall                         → WallFeedScreen      (Wall tab)
  /messages                     → InboxScreen         (Messages tab)
    /messages/:id               → ConversationScreen
  /dashboard                    → DashboardScreen     (Profile tab)
    /dashboard/profile          → ProfileEditScreen
    /dashboard/pigeons          → PigeonListScreen
      /dashboard/pigeons/add    → PigeonFormScreen (add)
      /dashboard/pigeons/:id    → PigeonDetailScreen
      /dashboard/pigeons/:id/edit → PigeonFormScreen (edit)
      /dashboard/pigeons/:id/pedigree → PedigreeTreeScreen
      /dashboard/pigeons/:id/pedigree/edit → PedigreeEditScreen
    /dashboard/listings         → MyListingsScreen
    /dashboard/saved            → SavedListingsScreen
    /dashboard/offers           → OffersScreen
    /dashboard/feed             → FeedGeneratorScreen

/notifications                  → NotificationsScreen (reachable via bell icon)
```

### Bottom Navigation Tabs (5 tabs)

| Index | Icon | Label | Root Route |
|---|---|---|---|
| 0 | store | Market | `/home` |
| 1 | gavel | Auctions | `/auctions` |
| 2 | dynamic_feed | Wall | `/wall` |
| 3 | chat_bubble | Messages | `/messages` |
| 4 | person | Me | `/dashboard` |

### Top AppBar (persistent across all tabs)
- Right: notification bell with unread badge → `/notifications`
- Badge count from `GET /api/notifications/count/` — poll every 60s while app is in foreground.

---

## API Integration

### Full Endpoint Reference

```dart
// core/constants/api_constants.dart
class ApiConstants {
  static String get baseUrl => dotenv.env['BASE_URL']!;

  // ── Auth ────────────────────────────────────────────────────────────────
  static const login          = '/auth/login/';
  static const refresh        = '/auth/refresh/';
  static const register       = '/auth/register/';
  static const me             = '/auth/me/';         // GET / PATCH

  // ── Pigeons ─────────────────────────────────────────────────────────────
  static const pigeons        = '/pigeons/';         // GET (mine) / POST
  static const breeds         = '/pigeons/breeds/';  // GET public
  static String pigeonDetail(int id) => '/pigeons/$id/';  // GET / PATCH / DELETE
  static String pigeonImages(int id) => '/pigeons/$id/images/';                // POST multipart {image,is_primary?,caption?}
  static String pigeonImageDelete(int id, int imgId) => '/pigeons/$id/images/$imgId/'; // DELETE

  // ── Marketplace ─────────────────────────────────────────────────────────
  static const marketplace         = '/marketplace/';         // GET (active) / POST
  static const myListings          = '/marketplace/mine/';    // GET
  static const savedListings       = '/marketplace/saved/';   // GET
  static const districts           = '/marketplace/districts/'; // GET — list of BD districts
  static const myOffers            = '/marketplace/offers/';  // GET sent+received
  static String listingDetail(int id)       => '/marketplace/$id/';
  static String toggleSave(int id)          => '/marketplace/$id/save/';        // POST
  static String makeOffer(int id)           => '/marketplace/$id/offer/';       // POST
  static String respondOffer(int offerId)   => '/marketplace/offers/$offerId/respond/'; // POST
  static String submitPayment(int offerId)  => '/marketplace/offers/$offerId/pay/';     // POST

  // ── Auctions ────────────────────────────────────────────────────────────
  static const auctions       = '/auctions/';        // GET ?status=live,upcoming,ended
  static String auctionDetail(int id) => '/auctions/$id/';   // GET
  static String placeBid(int id)      => '/auctions/$id/bid/';  // POST {amount}
  static String auctionPoll(int id)   => '/auctions/$id/poll/'; // GET — real-time state
  static String auctionWatch(int id)  => '/auctions/$id/watch/'; // POST toggle → {watching, watcher_count}

  // ── Wall ────────────────────────────────────────────────────────────────
  static const wallPosts       = '/wall/';           // GET last 30 posts
  static const wallCreate      = '/wall/create/';    // POST multipart {content, pigeon_id?, images[]}
  static String toggleLike(int postId)  => '/wall/$postId/like/';      // POST
  static String wallComments(int postId) => '/wall/$postId/comments/'; // GET list / POST {content}
  static String wallCommentDelete(int commentId) => '/wall/comment/$commentId/delete/'; // DELETE

  // ── Notifications ───────────────────────────────────────────────────────
  static const notifications      = '/notifications/';        // GET (marks all read)
  static const notificationCount  = '/notifications/count/';  // GET → {"count": N}

  // ── Pedigrees ───────────────────────────────────────────────────────────
  static String pedigree(int pigeonId)     => '/pedigree/$pigeonId/';
  static String pedigreeEdit(int pigeonId) => '/pedigree/$pigeonId/edit/';

  // ── Feed Generator ──────────────────────────────────────────────────────
  static const feedGenerate   = '/feed/generate/';   // GET ?purpose=&target_protein=

  // ── Messaging ───────────────────────────────────────────────────────────
  static const conversations  = '/messages/';
  static const startConversation = '/messages/start/';  // POST {listing_id} → {id, created}
  static String conversation(int id)  => '/messages/$id/';
  static String sendMessage(int id)   => '/messages/$id/send/';
}
```

### Authentication — JWT

| Token | Lifetime | Storage key |
|---|---|---|
| Access | 1 day | `access_token` |
| Refresh | 30 days | `refresh_token` |

`rotate_refresh_tokens = True` — a new refresh token is issued on every refresh call. Always persist the new one.

### Pagination

All list endpoints (marketplace, auctions, notifications…) return:
```json
{
  "count": 142,
  "next": "https://bdpigeonhub.com/api/marketplace/?page=2",
  "previous": null,
  "results": [...]
}
```
Implement **infinite scroll**: load first page on mount, append `results` when user reaches the bottom, stop when `next` is `null`.

### Marketplace Filters (query params)

| Param | Example | Notes |
|---|---|---|
| `search` | `?search=homer` | Searches title, pigeon name, breed |
| `breed` | `?breed=3` | Breed ID from `/pigeons/breeds/` |
| `district` | `?district=dhaka` | Value from `/marketplace/districts/` |
| `min_price` | `?min_price=5000` | BDT |
| `max_price` | `?max_price=20000` | BDT |
| `ordering` | `?ordering=-created_at` | `price`, `-price`, `created_at`, `views_count` |

### Auction Filter (query params)

| Param | Values |
|---|---|
| `status` | `live`, `upcoming`, `ended`, `cancelled` (comma-separated OK: `live,upcoming`) |
| `search` | Searches title, seller username |
| `ordering` | `end_time`, `created_at`, `bid_count` |

### Make Offer — request body
```json
{ "amount": "15000.00", "message": "Is this negotiable?" }
```

### Respond to Offer — request body
```json
{ "action": "accept" }
// or
{ "action": "reject" }
// or
{ "action": "counter", "counter_amount": "13000.00", "counter_msg": "Best I can do" }
```

### Submit Payment — request body
```json
{ "method": "bkash", "trx_id": "AB12345678" }
// method options: "bkash" | "nagad" | "rocket"
```

### Place Bid — request body
```json
{ "amount": "12500.00" }
```
Response includes `extended: true` if the anti-snipe window fired and `end_time` was extended.

### Auction Poll — response shape
```json
{
  "status": "live",
  "current_price": "12500.00",
  "bid_count": 7,
  "end_seconds": 342,
  "end_time": "2026-06-06T18:30:00+06:00",
  "winner": null,
  "top_bidder": "racer99",
  "min_bid": "12550.00",
  "reserve_met": true
}
```
Poll this endpoint every **3–5 seconds** while `AuctionDetailScreen` is open. Stop polling when `status` is `ended` or `cancelled`.

---

## Data Models

> ⚠️ **Reference shapes only.** The snippets below are written in `freezed` syntax to document the exact JSON field names and types returned by the API. The actual app does **not** use freezed — implement each as a plain Dart class with a hand-written `factory Model.fromJson(Map<String, dynamic> json)` (see the existing `ListingModel` / `AuctionModel` / `WallPostModel` in `BHP_Flutter/lib/features/.../data/models/` for the established pattern). Keep the same JSON key mappings shown here.

### User
```dart
@freezed
class User with _$User {
  factory User({
    required int id,
    required String username,
    required String email,
    @JsonKey(name: 'first_name') String? firstName,
    @JsonKey(name: 'last_name') String? lastName,
    String? phone,
    String? location,
    String? bio,
    String? avatar,
    @JsonKey(name: 'is_verified') required bool isVerified,
    String? language,                            // 'en' | 'bn'
    @JsonKey(name: 'avg_rating') double? avgRating,
    @JsonKey(name: 'follower_count') int? followerCount,
    @JsonKey(name: 'following_count') int? followingCount,
  }) = _User;
  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
}
```

### PigeonImage
```dart
@freezed
class PigeonImage with _$PigeonImage {
  factory PigeonImage({
    required int id,
    required String image,
    @JsonKey(name: 'is_primary') required bool isPrimary,
    String? caption,
    @JsonKey(name: 'edit_score') int? editScore,    // 0-100; null = not yet analysed
    @JsonKey(name: 'edit_notes') String? editNotes, // human-readable signals
    @JsonKey(name: 'edit_label') String? editLabel, // 'Raw' | '42% edited'
  }) = _PigeonImage;
  factory PigeonImage.fromJson(Map<String, dynamic> json) => _$PigeonImageFromJson(json);
}
```

### Pigeon
```dart
@freezed
class Pigeon with _$Pigeon {
  factory Pigeon({
    required int id,
    required String name,
    @JsonKey(name: 'ring_number') String? ringNumber,
    required String gender,       // 'M' | 'F' | 'U'
    required String color,
    int? breed,
    @JsonKey(name: 'breed_name') String? breedName,
    @JsonKey(name: 'date_of_birth') String? dateOfBirth,
    @JsonKey(name: 'age_display') String? ageDisplay,
    double? weight,
    String? description,
    @JsonKey(name: 'is_for_sale') required bool isForSale,
    required int owner,
    @JsonKey(name: 'owner_name') String? ownerName,
    List<PigeonImage>? images,
    @JsonKey(name: 'created_at') required String createdAt,
  }) = _Pigeon;
  factory Pigeon.fromJson(Map<String, dynamic> json) => _$PigeonFromJson(json);
}
```

### Listing
```dart
@freezed
class Listing with _$Listing {
  factory Listing({
    required int id,
    required String title,
    required String description,
    required String price,
    required String location,
    required String district,                         // 'dhaka', 'chittagong', etc.
    @JsonKey(name: 'district_label') String? districtLabel, // 'Dhaka', 'Chittagong', etc.
    required String status,                           // 'active'|'sold'|'reserved'|'inactive'
    @JsonKey(name: 'is_negotiable') required bool isNegotiable,
    @JsonKey(name: 'views_count') required int viewsCount,
    required Pigeon pigeon,
    required int seller,
    @JsonKey(name: 'seller_id') int? sellerId,
    @JsonKey(name: 'seller_name') String? sellerName,
    @JsonKey(name: 'seller_avatar') String? sellerAvatar,
    @JsonKey(name: 'is_saved') required bool isSaved,
    @JsonKey(name: 'created_at') required String createdAt,
  }) = _Listing;
  factory Listing.fromJson(Map<String, dynamic> json) => _$ListingFromJson(json);
}
```

### Offer
```dart
@freezed
class Offer with _$Offer {
  factory Offer({
    required int id,
    required int listing,
    @JsonKey(name: 'listing_title') String? listingTitle,
    @JsonKey(name: 'listing_price') String? listingPrice,
    @JsonKey(name: 'listing_image') String? listingImage,
    required int buyer,
    @JsonKey(name: 'buyer_name') String? buyerName,
    required String amount,
    String? message,
    required String status,         // 'pending'|'accepted'|'rejected'|'countered'|'withdrawn'
    @JsonKey(name: 'counter_amount') String? counterAmount,
    @JsonKey(name: 'counter_msg') String? counterMsg,
    @JsonKey(name: 'payment_status') String? paymentStatus,  // null|'pending'|'confirmed'|'disputed'
    @JsonKey(name: 'created_at') required String createdAt,
    @JsonKey(name: 'updated_at') required String updatedAt,
  }) = _Offer;
  factory Offer.fromJson(Map<String, dynamic> json) => _$OfferFromJson(json);
}
```

### Auction
```dart
@freezed
class Auction with _$Auction {
  factory Auction({
    required int id,
    required String title,
    required String description,
    @JsonKey(name: 'seller_name') required String sellerName,
    @JsonKey(name: 'cover_image') String? coverImage,
    @JsonKey(name: 'starting_price') required String startingPrice,
    @JsonKey(name: 'display_price') required String displayPrice,  // current or starting
    @JsonKey(name: 'reserve_price') String? reservePrice,          // hidden; may be null
    @JsonKey(name: 'min_increment') required String minIncrement,
    @JsonKey(name: 'bid_count') required int bidCount,
    @JsonKey(name: 'views_count') required int viewsCount,
    @JsonKey(name: 'start_time') required String startTime,
    @JsonKey(name: 'end_time') required String endTime,
    required String status,         // 'upcoming'|'live'|'ended'|'cancelled'
    @JsonKey(name: 'pigeon_name') String? pigeonName,
    @JsonKey(name: 'breed_name') String? breedName,
    @JsonKey(name: 'winner_name') String? winnerName,
    @JsonKey(name: 'reserve_met') bool? reserveMet,
    @JsonKey(name: 'pedigree_image_url') String? pedigreeImageUrl,
    List<AuctionImage>? gallery,

    // Detail only (from AuctionDetailScreen)
    List<Bid>? bids,
    @JsonKey(name: 'min_next_bid') String? minNextBid,
    @JsonKey(name: 'is_watching') bool? isWatching,
    @JsonKey(name: 'is_top_bidder') bool? isTopBidder,
  }) = _Auction;
  factory Auction.fromJson(Map<String, dynamic> json) => _$AuctionFromJson(json);
}

@freezed
class Bid with _$Bid {
  factory Bid({
    required int id,
    @JsonKey(name: 'bidder_name') required String bidderName,
    required String amount,
    @JsonKey(name: 'created_at') required String createdAt,
  }) = _Bid;
  factory Bid.fromJson(Map<String, dynamic> json) => _$BidFromJson(json);
}

@freezed
class AuctionImage with _$AuctionImage {
  factory AuctionImage({
    required int id,
    required String image,
    int? order,
  }) = _AuctionImage;
  factory AuctionImage.fromJson(Map<String, dynamic> json) => _$AuctionImageFromJson(json);
}
```

### AuctionPoll (ephemeral — not persisted, just refreshed)
```dart
@freezed
class AuctionPoll with _$AuctionPoll {
  factory AuctionPoll({
    required String status,
    @JsonKey(name: 'current_price') required String currentPrice,
    @JsonKey(name: 'bid_count') required int bidCount,
    @JsonKey(name: 'end_seconds') required int endSeconds,
    @JsonKey(name: 'end_time') required String endTime,
    String? winner,
    @JsonKey(name: 'top_bidder') String? topBidder,
    @JsonKey(name: 'min_bid') required String minBid,
    @JsonKey(name: 'reserve_met') required bool reserveMet,
  }) = _AuctionPoll;
  factory AuctionPoll.fromJson(Map<String, dynamic> json) => _$AuctionPollFromJson(json);
}
```

### Post & Wall
```dart
@freezed
class PostImage with _$PostImage {
  factory PostImage({
    required int id,
    required String image,
    int? order,
    @JsonKey(name: 'edit_score') int? editScore,
    @JsonKey(name: 'edit_notes') String? editNotes,
    @JsonKey(name: 'edit_label') String? editLabel,
  }) = _PostImage;
  factory PostImage.fromJson(Map<String, dynamic> json) => _$PostImageFromJson(json);
}

@freezed
class Post with _$Post {
  factory Post({
    required int id,
    required String content,
    @JsonKey(name: 'author_name') required String authorName,
    @JsonKey(name: 'author_avatar') String? authorAvatar,
    @JsonKey(name: 'pigeon_name') String? pigeonName,
    List<PostImage>? images,
    @JsonKey(name: 'like_count') required int likeCount,
    @JsonKey(name: 'comment_count') required int commentCount,
    @JsonKey(name: 'is_liked') required bool isLiked,
    @JsonKey(name: 'created_at') required String createdAt,
  }) = _Post;
  factory Post.fromJson(Map<String, dynamic> json) => _$PostFromJson(json);
}
```

### Notification
```dart
@freezed
class AppNotification with _$AppNotification {
  factory AppNotification({
    required int id,
    @JsonKey(name: 'notif_type') required String notifType,
    // notifType values: like | comment | follow | offer_received | offer_accepted |
    //                   offer_rejected | offer_countered | review | message |
    //                   payment | contest_winner
    required String icon,             // emoji, from backend
    required String message,
    required String url,              // deep-link path e.g. '/auctions/5/'
    @JsonKey(name: 'is_read') required bool isRead,
    @JsonKey(name: 'actor_name') String? actorName,
    @JsonKey(name: 'actor_avatar') String? actorAvatar,
    @JsonKey(name: 'created_at') required String createdAt,
  }) = _AppNotification;
  factory AppNotification.fromJson(Map<String, dynamic> json) => _$AppNotificationFromJson(json);
}
```

### FeedResult
```dart
@freezed
class FeedResult with _$FeedResult {
  factory FeedResult({
    required String purpose,
    required List<FeedItem> items,
    @JsonKey(name: 'total_protein') required double totalProtein,
    @JsonKey(name: 'total_fat') required double totalFat,
    @JsonKey(name: 'total_carbs') required double totalCarbs,
    @JsonKey(name: 'total_fiber') required double totalFiber,
    @JsonKey(name: 'total_cal') required double totalCal,
    required Map<String, dynamic> targets,
  }) = _FeedResult;
  factory FeedResult.fromJson(Map<String, dynamic> json) => _$FeedResultFromJson(json);
}
```

### PedigreeRecord
```dart
@freezed
class PedigreeRecord with _$PedigreeRecord {
  factory PedigreeRecord({
    required int id,
    required int pigeon,
    int? sire,
    @JsonKey(name: 'sire_detail') Pigeon? sireDetail,
    int? dam,
    @JsonKey(name: 'dam_detail') Pigeon? damDetail,
    String? notes,
    @JsonKey(name: 'is_public') required bool isPublic,
  }) = _PedigreeRecord;
  factory PedigreeRecord.fromJson(Map<String, dynamic> json) => _$PedigreeRecordFromJson(json);
}
```

---

## State Management

> ⚠️ **Reference logic only.** Snippets use `@riverpod` codegen syntax to convey intent. Implement with **manual** providers — e.g. `StateNotifierProvider` for auth (see `auth_provider.dart`), `FutureProvider.autoDispose` / `.family` for fetches (see `marketplace_providers.dart`), and a plain `Timer.periodic` inside a `StateNotifier` for auction polling. The polling/refresh behaviour described below still applies.

### Auth State
```dart
@riverpod
class AuthNotifier extends _$AuthNotifier {
  @override
  Future<User?> build() async {
    final token = await ref.read(secureStorageProvider).getAccessToken();
    if (token == null) return null;
    return ref.read(authRepositoryProvider).getMe();
  }

  Future<void> login(String username, String password) async { ... }
  Future<void> register(Map<String, dynamic> data) async { ... }
  Future<void> logout() async { ... }
}
```

### Marketplace with Filters
```dart
@freezed
class ListingFilter with _$ListingFilter {
  factory ListingFilter({
    String? search,
    int? breedId,
    String? district,    // 'dhaka' | 'chittagong' | etc.
    double? minPrice,
    double? maxPrice,
    String? ordering,
  }) = _ListingFilter;
}
```

### Auction — Live Polling
```dart
@riverpod
class AuctionDetailNotifier extends _$AuctionDetailNotifier {
  Timer? _pollTimer;

  @override
  Future<Auction> build(int auctionId) async {
    ref.onDispose(() => _pollTimer?.cancel());
    final auction = await ref.read(auctionRepositoryProvider).getDetail(auctionId);
    if (auction.status == 'live') _startPolling(auctionId);
    return auction;
  }

  void _startPolling(int id) {
    _pollTimer = Timer.periodic(const Duration(seconds: 4), (_) async {
      final poll = await ref.read(auctionRepositoryProvider).poll(id);
      // Update price, bidCount, endTime in state
      state = state.whenData((a) => a.copyWith(
        displayPrice: poll.currentPrice,
        bidCount: poll.bidCount,
        endTime: poll.endTime,
        status: poll.status,
      ));
      if (poll.status != 'live') _pollTimer?.cancel();
    });
  }

  Future<Map<String, dynamic>> placeBid(int auctionId, String amount) async {
    final result = await ref.read(auctionRepositoryProvider).bid(auctionId, amount);
    ref.invalidateSelf();
    return result;
  }
}
```

### Notifications — Unread Count Badge
```dart
@riverpod
class NotificationCountNotifier extends _$NotificationCountNotifier {
  Timer? _timer;

  @override
  Future<int> build() async {
    ref.onDispose(() => _timer?.cancel());
    _timer = Timer.periodic(const Duration(seconds: 60), (_) => ref.invalidateSelf());
    return ref.read(notificationRepositoryProvider).getUnreadCount();
  }
}
```

---

## Screen Descriptions

### AuctionListScreen
- Two sections: **Live** (sorted by soonest ending) and **Upcoming**
- Each card: cover image, title, current price, bid count, countdown timer
- Filter tabs: All / Live / Upcoming / Ended
- Tap → `AuctionDetailScreen`

### AuctionDetailScreen
- Image gallery (cover + gallery images)
- Pedigree image if available
- Live countdown timer (days:hours:mins:secs), turns red under 60s
- Current price, bid count, min next bid, reserve met indicator
- Bid history list (last 20 bids)
- Bid input field + "Place Bid" button (disabled if auction not live or user is seller)
- On successful bid: show snackbar, refresh state via poll
- Anti-snipe notice: if `extended: true` in bid response, show "Auction extended!" toast
- When `status == 'ended'`: show winner name, disable bid input, stop polling

### WallFeedScreen
- Infinite scroll list of posts (load first 30, API doesn't paginate wall — fetch all)
- Each post: author avatar/name/time, content text, images grid, pigeon tag chip, like/comment counts
- **Image authenticity badge**: each image shows `edit_label` (e.g. "📷 Raw" or "✏️ 42% edited") in a colour-coded chip:
  - 0–20: green ("Raw")
  - 21–50: yellow
  - 51–75: orange
  - 76–100: red
- Like button: optimistic toggle, POST `/api/wall/<id>/like/`
- "Create Post" FAB → `CreatePostScreen`

### CreatePostScreen
- Text field for content
- Image picker (up to 4 images)
- Pigeon tag picker (list of user's own pigeons)
- Submit as `multipart/form-data` POST to `/wall/post/` (web URL, not API — see note below)

### NotificationsScreen
- Grouped list, newest first
- Icon, message, actor avatar, timestamp
- Tap → deep-link to the relevant screen using `url` field (parse `/auctions/5/` → push `AuctionDetailScreen(id:5)`)
- On screen open: all notifications marked read automatically by the GET `/api/notifications/`

### OffersScreen
- Two tabs: **Sent** / **Received**
- Each offer card: listing thumbnail, title, offer amount, status badge
- Received tab: Accept / Reject / Counter action buttons
- If accepted: show "Submit Payment" form (method picker + TXN ID field)
- Payment status badge: pending / confirmed / disputed

### ListingDetailScreen (updated)
- Now shows `district_label` and `is_saved` toggle
- "Make Offer" button → offer bottom sheet (amount + message fields)
- Seller avatar from `seller_avatar`

---

## Development Phases

Progress as of 2026-06-07: **Phases 1, 2, 3, 4, 5 complete. Phases 6–11 pending.**
(Phase numbers below were re-grouped from the as-built milestones M1–M4. "Phase 3 — Home" was added because the home dashboard was built ahead of the standalone Pigeons CRUD, which moves to Phase 5.)

### Phase 1 — Foundation ✅ DONE
- [x] Flutter project setup (`BHP_Flutter/`, org `com.bdpigeonhub`)
- [x] Add dependencies to `pubspec.yaml` (manual-provider stack — no codegen)
- [x] `AppConfig` enum for base URL (replaces `.env`/dotenv)
- [x] `ApiClient` (Dio) with auth interceptor + 401 auto-refresh + typed `AppException` mapping
- [x] `SecureStorage` wrapper (access/refresh/userId/username)
- [x] `GoRouter` with `ShellRoute`, auth redirect guard, `_AuthListenable` Riverpod→router bridge
- [x] `MainShell` (5-tab bottom nav: Home / Market / Auctions / Wall / Profile)
- [x] Core widgets: `AppButton`, `AppAvatar`, `LoadingShimmer*`, `EmptyState`, `ErrorState`
- [x] `AppTheme` (orange #ea580c) + `AppColors`
- ~~Run `build_runner`~~ — N/A (codegen removed)

### Phase 2 — Authentication ✅ DONE
- [x] `UserModel` (manual `fromJson`, `displayName` getter)
- [x] `AuthRepository` (login → JWT pair + GET /me/, register → auto-login, fetchMe, updateProfile)
- [x] `AuthNotifier` (`StateNotifier<AuthState>`) — boot-from-cache, login, register, logout
- [x] `SplashScreen`, `LoginScreen`, `RegisterScreen`, `ForgotPasswordScreen` (opens web reset in browser)
- [ ] `ProfileEditScreen` — deferred to Phase 9 (Profile)

### Phase 3 — Home ✅ DONE
- [x] `ListingModel`, `AuctionModel`, `WallPostModel` (manual `fromJson`)
- [x] `HomeRepository` + `FutureProvider`s (featured listings, live auctions, wall posts, notif count)
- [x] `HomeScreen`: hero search, stats strip, live-auction horizontal strip with 1s countdown, featured listings grid, wall preview grid, guest CTA
- [x] Notification bell with unread-count badge in AppBar
- [x] Pull-to-refresh invalidates all home providers
- [x] Backend: added `/api/auctions/`, `/api/wall/`, `/api/notifications/count/`

### Phase 4 — Marketplace ✅ DONE
- [x] `MarketplaceFilter`, `DistrictModel`, `OfferModel`; extended `ListingModel` (district, sellerAvatar, isSaved)
- [x] `MarketplaceRepository` (list+filters, detail, mine, saved, toggleSave, makeOffer, fetchMyOffers, respondOffer, submitPayment, fetchDistricts)
- [x] Providers: `listingsProvider` (filter-reactive), `listingDetailProvider(id)`, `myListingsProvider`, `districtsProvider`, `myOffersProvider`
- [x] `MarketplaceScreen` — 2-col grid, search, filter bottom sheet (sort + district chips + price range), active filter chips
- [x] `ListingDetailScreen` — PageView gallery with dots, pigeon spec grid, seller chip, save toggle, bottom CTA bar
- [x] `MakeOfferScreen` — amount + message
- [x] `MyOffersScreen` — tabbed Sent/Received, accept/reject/counter, bKash/Nagad/Rocket payment sheet
- [x] Backend: enhanced listing serializer + full offer/save/district API
- [ ] `AddListingScreen` — deferred (needs Pigeons CRUD from Phase 5 first)
- [ ] `SavedListingsScreen` standalone screen (API ready)

### Phase 5 — Pigeons (My Flock) ✅ DONE
- [x] `Pigeon`, `BreedModel`, `PigeonImage` models (full, with `editScore`/`editNotes`/`editLabel`) in `features/pigeons/data/models/pigeon_models.dart`
- [x] `PigeonRepository` — list, detail, create, update, delete, fetchBreeds, uploadImage (multipart), deleteImage
- [x] Providers: `myPigeonsProvider`, `pigeonDetailProvider(id)`, `breedsProvider`
- [x] `EditScoreBadge` shared widget (`core/widgets/edit_score_badge.dart`, colour-coded 0–20/21–50/51–75/76–100)
- [x] `PigeonListScreen` — cards w/ thumbnail, breed/gender/age, for-sale chip, FAB, pull-to-refresh, empty state
- [x] `PigeonDetailScreen` — horizontal photo gallery w/ edit-score badges, add/delete photos (image_picker), primary badge, spec grid, edit/delete via popup menu
- [x] `PigeonFormScreen` (add + edit) — name/ring/breed dropdown/gender/color/DOB date-picker/weight/description; photo pick on add
- [x] `MeScreen` (Profile tab) entry point → My Pigeons + My Offers + Logout
- [x] `POST/DELETE /api/pigeons/<id>/images/` backend endpoints (added 2026-06-07)
- [ ] Wire `AddListingScreen` (dual-mode) — deferred into Phase 4 marketplace follow-up (pigeon picker now available)
- [x] Build verified: `flutter build apk --debug` passes

### Phase 6 — Auctions ⬜ NEXT
- [ ] `AuctionModel` (full detail), `BidModel`, `AuctionImageModel`, `AuctionPoll`
- [ ] `AuctionRepository` (list, detail, bid, poll)
- [ ] `AuctionDetailNotifier` with `Timer.periodic` polling every 4s (stop when ended/cancelled)
- [ ] `AuctionListScreen` (Live / Upcoming / Ended tabs)
- [ ] `AuctionDetailScreen` (gallery, countdown turning red <60s, bid form, bid history, anti-snipe toast)
- [ ] 🚧 optional backend: `POST /api/auctions/<id>/watch/` for the watch feature

### Phase 7 — Wall ⬜
- [ ] `PostModel`, `PostImageModel` (with `editScore`/`editLabel`), `CommentModel`
- [ ] `WallRepository` (get posts, toggle like)
- [ ] `WallFeedScreen` — like toggle (optimistic) + image authenticity badges
- [ ] `CreatePostScreen` (text + up to 4 images + pigeon tag)
- [ ] 🚧 needs backend: `POST /api/wall/` multipart create; `GET/POST /api/wall/<id>/comment(s)/`

### Phase 8 — Notifications ⬜
- [ ] `AppNotification` model
- [ ] `NotificationRepository` (list, count)
- [ ] `NotificationsScreen` with deep-link routing on tap (parse `url` → push screen)
- [x] Unread-count badge already live on Home AppBar (Phase 3)

### Phase 9 — Profile & Social ⬜
- [ ] `ProfileEditScreen` (avatar, bio, location, phone)
- [ ] Public profile screen (listings, won auctions, reviews, follower stats)
- [ ] Follow / unfollow
- [ ] `DashboardScreen` (counts + recent conversations)
- [ ] 🚧 needs backend: profile/follow/review API endpoints (currently web-only)

### Phase 10 — Messaging ⬜
- [ ] `Conversation`, `Message` models
- [ ] `MessagingRepository`, `InboxScreen`, `ConversationScreen` (30s refresh)
- [x] API ready: `GET /api/messages/`, `GET /api/messages/<id>/`, `POST /api/messages/<id>/send/`
- [ ] 🚧 only gap: start-conversation is web-only (`/messages/start/<listing_id>/`) — needs `POST /api/messages/start/`

### Phase 11 — Secondary & Polish ⬜
- [ ] Pedigrees (tree view + edit) — API ready: `GET/POST /api/pedigree/<pigeon_id>/` + `/edit/`
- [ ] Feed Generator screen — API ready: `GET /api/feed/generate/?purpose=&target_protein=`
- [ ] Contests (list, enter, vote) — 🚧 needs API
- [ ] Loading skeletons / empty / error states across all screens (pattern already in core widgets)
- [ ] Offline cache with `hive_flutter`
- [ ] Bengali (bn) language toggle to match web
- [ ] FCM push notifications (needs backend device-token endpoint)
- [ ] App icon + native splash, Android/iOS build config, Play Store / App Store prep

---

## Running the App

```bash
cd "F:\AlphaCue Technologies\BPH\BHP_Flutter"

# Install dependencies
flutter pub get

# (No code generation — models & providers are hand-written, no build_runner)

# Run on connected device or emulator
flutter run

# Static analysis (should show only info-level hints, zero errors)
flutter analyze

# Build APK
flutter build apk --release

# Build AAB for Play Store
flutter build appbundle --release
```

### Android Manifest Requirements

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />
<uses-permission android:name="android.permission.CAMERA" />
```

### Connecting to Local Dev Server

| Device | Base URL |
|---|---|
| Android Emulator | `http://10.0.2.2:8000/api` |
| Physical Device (USB) | `http://<LAN-IP>:8000/api` |
| iOS Simulator | `http://localhost:8000/api` |
| Production | `https://bdpigeonhub.com/api` |

---

## Backend Coordination Notes

### Resolved since last sync
- ✅ **Save listing** endpoint: `POST /api/marketplace/<id>/save/` → `{"saved": bool, "save_count": N}`
- ✅ **District filter**: `GET /api/marketplace/districts/` → `[{"value": "dhaka", "label": "Dhaka"}, ...]`
- ✅ **My listings / saved listings**: `/api/marketplace/mine/` and `/api/marketplace/saved/`
- ✅ **Pedigree API**: `GET/POST /api/pedigree/<pigeon_id>/` and `/api/pedigree/<pigeon_id>/edit/`
- ✅ **Feed Generator API**: `GET /api/feed/generate/?purpose=&target_protein=`
- ✅ **Messaging API**: `GET /api/messages/`, `GET /api/messages/<id>/`, `POST /api/messages/<id>/send/`

### Resolved 2026-06-07 — the 5 previously-missing endpoints are now live
- ✅ **Wall post create** — `POST /api/wall/create/` (multipart: `content`, optional `pigeon_id`, `images[]`). Returns the created post (PostListSerializer shape).
- ✅ **Wall comments** — `GET /api/wall/<post_id>/comments/` (list) and `POST /api/wall/<post_id>/comments/` (body `{content}`). Delete own: `DELETE /api/wall/comment/<comment_id>/delete/`. Posting notifies the post author.
- ✅ **Conversation start** — `POST /api/messages/start/` body `{ "listing_id": N }` → `{ "id": <conversationId>, "created": bool }`. Finds an existing buyer↔seller conversation for that listing or creates one. Then open it via `GET /api/messages/<id>/`.
- ✅ **Pigeon image upload** — `POST /api/pigeons/<id>/images/` (multipart: `image`, optional `is_primary`, `caption`). First image auto-becomes primary. Delete: `DELETE /api/pigeons/<id>/images/<image_id>/` (auto-promotes another image to primary). Response includes `edit_score`/`edit_label` from the authenticity analyzer.
- ✅ **Auction watch** — `POST /api/auctions/<id>/watch/` toggles → `{ "watching": bool, "watcher_count": N }`. (Detail endpoint already returns `is_watching`.)

### Still needed from backend (not yet API; web-only)
- ⚠️ **Contests** — list / enter / vote are web-only.
- ⚠️ **Public profile / follow / reviews** — web-only; no `/api/users/<username>/` profile, follow-toggle, or review endpoints yet.

### Image Authenticity Badge
Every `PigeonImage` and `PostImage` object now returns three extra fields:
- `edit_score` — int 0–100 (null if not yet analysed, e.g. old images)
- `edit_notes` — semicolon-separated explanation string
- `edit_label` — display string: `"Raw"` (score ≤ 20) or `"42% edited"` (score > 20)

Display with the `EditScoreBadge` widget. Colour guide:
- 0–20 → green chip ("📷 Raw")
- 21–50 → yellow chip ("✏️ X%")
- 51–75 → orange chip ("✏️ X%")
- 76–100 → red chip ("✏️ X%")

### CORS
`CORS_ALLOW_ALL_ORIGINS = True` — open in production. No special headers required.

### API vs Web URLs
The backend serves both web pages (Django templates) and REST API (`/api/`). Always use `/api/` paths from Flutter — never call web page URLs directly.

### reCAPTCHA
reCAPTCHA v3 is active on all web forms. The REST API endpoints are **not** protected by reCAPTCHA — JWT authentication is sufficient for the mobile app. No captcha handling needed in Flutter.

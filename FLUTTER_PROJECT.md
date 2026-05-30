# BD Pigeon Hub — Flutter App

Flutter mobile client for the Bangladesh Pigeon Hub platform. Consumes the Django REST API (`/api/`) with JWT authentication.

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

---

## Features

| Module | Features |
|---|---|
| **Auth** | Register, login, logout, JWT token refresh, profile edit |
| **Marketplace** | Browse listings, filter by breed/price/location/search, listing detail, create listing, save listing |
| **My Pigeons** | List, add, edit, delete pigeons; image upload; pigeon detail |
| **Pedigrees** | View multi-generation family tree (sire/dam), edit pedigree links |
| **Feed Generator** | Select purpose + optional protein target → grain mix with nutritional breakdown |
| **Messaging** | Inbox, 1-to-1 conversation view, send messages |
| **Dashboard** | Pigeon count, active listing count, unread message count, recent conversations |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Flutter 3.x (Dart 3.x) |
| State Management | Riverpod (`flutter_riverpod` + `riverpod_annotation`) |
| Navigation | `go_router` |
| HTTP Client | `dio` |
| Token Storage | `flutter_secure_storage` |
| Image Caching | `cached_network_image` |
| Image Picking | `image_picker` |
| Model Codegen | `freezed` + `json_serializable` |
| Date Formatting | `intl` |
| Environment | `flutter_dotenv` |

---

## Project Structure

```
lib/
├── main.dart
├── app.dart                        # MaterialApp + GoRouter setup
├── core/
│   ├── constants/
│   │   ├── api_constants.dart      # Base URL, endpoint paths
│   │   └── app_constants.dart      # Colors, text styles, sizes
│   ├── network/
│   │   ├── dio_client.dart         # Dio instance + interceptors
│   │   └── api_exception.dart      # Error model
│   ├── storage/
│   │   └── secure_storage.dart     # JWT token read/write/clear
│   ├── router/
│   │   └── app_router.dart         # GoRouter routes & guards
│   └── widgets/
│       ├── loading_indicator.dart
│       ├── error_view.dart
│       ├── pigeon_card.dart
│       └── listing_card.dart
├── features/
│   ├── auth/
│   │   ├── data/
│   │   │   ├── auth_repository.dart
│   │   │   └── models/
│   │   │       ├── user.dart
│   │   │       ├── user.freezed.dart
│   │   │       └── user.g.dart
│   │   ├── providers/
│   │   │   └── auth_provider.dart
│   │   └── screens/
│   │       ├── splash_screen.dart
│   │       ├── login_screen.dart
│   │       └── register_screen.dart
│   ├── dashboard/
│   │   ├── data/
│   │   │   └── dashboard_repository.dart
│   │   ├── providers/
│   │   │   └── dashboard_provider.dart
│   │   └── screens/
│   │       └── dashboard_screen.dart
│   ├── pigeons/
│   │   ├── data/
│   │   │   ├── pigeon_repository.dart
│   │   │   └── models/
│   │   │       ├── pigeon.dart
│   │   │       ├── pigeon.freezed.dart
│   │   │       ├── pigeon.g.dart
│   │   │       ├── breed.dart
│   │   │       └── pigeon_image.dart
│   │   ├── providers/
│   │   │   └── pigeon_provider.dart
│   │   └── screens/
│   │       ├── pigeon_list_screen.dart
│   │       ├── pigeon_detail_screen.dart
│   │       └── pigeon_form_screen.dart
│   ├── marketplace/
│   │   ├── data/
│   │   │   ├── marketplace_repository.dart
│   │   │   └── models/
│   │   │       └── listing.dart
│   │   ├── providers/
│   │   │   └── marketplace_provider.dart
│   │   └── screens/
│   │       ├── listing_list_screen.dart
│   │       ├── listing_detail_screen.dart
│   │       ├── add_listing_screen.dart
│   │       └── my_listings_screen.dart
│   ├── pedigrees/
│   │   ├── data/
│   │   │   ├── pedigree_repository.dart
│   │   │   └── models/
│   │   │       └── pedigree_record.dart
│   │   ├── providers/
│   │   │   └── pedigree_provider.dart
│   │   └── screens/
│   │       ├── pedigree_tree_screen.dart
│   │       └── pedigree_edit_screen.dart
│   ├── feed_generator/
│   │   ├── data/
│   │   │   ├── feed_repository.dart
│   │   │   └── models/
│   │   │       └── feed_result.dart
│   │   ├── providers/
│   │   │   └── feed_provider.dart
│   │   └── screens/
│   │       └── feed_generator_screen.dart
│   └── messaging/
│       ├── data/
│       │   ├── messaging_repository.dart
│       │   └── models/
│       │       ├── conversation.dart
│       │       └── message.dart
│       ├── providers/
│       │   └── messaging_provider.dart
│       └── screens/
│           ├── inbox_screen.dart
│           └── conversation_screen.dart
└── shared/
    └── main_shell.dart             # Bottom navigation shell
```

---

## Dependencies

Add to `pubspec.yaml`:

```yaml
dependencies:
  flutter:
    sdk: flutter

  # Networking
  dio: ^5.7.0

  # State management
  flutter_riverpod: ^2.6.1
  riverpod_annotation: ^2.6.1

  # Navigation
  go_router: ^14.6.3

  # Secure storage (JWT tokens)
  flutter_secure_storage: ^9.2.2

  # Image handling
  cached_network_image: ^3.4.1
  image_picker: ^1.1.2

  # Model generation
  freezed_annotation: ^2.4.4
  json_annotation: ^4.9.0

  # Utilities
  intl: ^0.19.0
  flutter_dotenv: ^5.2.1

dev_dependencies:
  flutter_test:
    sdk: flutter
  build_runner: ^2.4.13
  freezed: ^2.5.7
  json_serializable: ^6.8.0
  riverpod_generator: ^2.6.3
  custom_lint: ^0.7.5
  riverpod_lint: ^2.6.3
```

---

## Environment Setup

Create `.env` in the Flutter project root:

```env
BASE_URL=http://192.168.1.XXX:8000/api
# Use your machine's LAN IP when running on a physical device.
# Use http://10.0.2.2:8000/api for Android Emulator (maps to host localhost).
```

Load in `main.dart`:

```dart
await dotenv.load(fileName: '.env');
```

Add to `assets` in `pubspec.yaml`:

```yaml
flutter:
  assets:
    - .env
```

---

## Architecture

The app uses a **feature-first repository pattern** with Riverpod:

```
Screen → Provider (AsyncNotifier) → Repository → DioClient → API
                                  ↑
                              SecureStorage (tokens)
```

- **Screens** are pure UI — they watch providers.
- **Providers** (`AsyncNotifier` / `FutureProvider`) hold state and call repositories.
- **Repositories** contain all API call logic and return typed model objects.
- **DioClient** is a singleton Dio instance with two interceptors:
  1. **Auth Interceptor** — attaches `Authorization: Bearer <token>` header to every request.
  2. **Refresh Interceptor** — on 401, silently refreshes the token via `/api/auth/refresh/` and retries.

---

## Screens & Navigation

### Route Map (`go_router`)

```
/splash                   → SplashScreen
/login                    → LoginScreen
/register                 → RegisterScreen

/ (ShellRoute — Bottom Nav)
  /home                   → ListingListScreen (Marketplace tab)
  /pigeons                → PigeonListScreen
    /pigeons/add          → PigeonFormScreen (add)
    /pigeons/:id          → PigeonDetailScreen
    /pigeons/:id/edit     → PigeonFormScreen (edit)
    /pigeons/:id/pedigree → PedigreeTreeScreen
    /pigeons/:id/pedigree/edit → PedigreeEditScreen
  /feed                   → FeedGeneratorScreen
  /messages               → InboxScreen
    /messages/:id         → ConversationScreen
  /dashboard              → DashboardScreen
    /dashboard/profile    → ProfileEditScreen
    /dashboard/listings   → MyListingsScreen
    /marketplace/add      → AddListingScreen

/marketplace/:id          → ListingDetailScreen (accessible from home tab)
```

### Bottom Navigation Tabs (5 tabs)

| Index | Icon | Label | Root Route |
|---|---|---|---|
| 0 | store | Marketplace | `/home` |
| 1 | pets | My Pigeons | `/pigeons` |
| 2 | grass | Feed | `/feed` |
| 3 | chat_bubble | Messages | `/messages` |
| 4 | person | Dashboard | `/dashboard` |

### Route Guard

In `GoRouter.redirect`: if no token in `SecureStorage`, redirect to `/login` for any protected route. Splash screen triggers the check on cold start.

---

## API Integration

### Base URL

```dart
// core/constants/api_constants.dart
class ApiConstants {
  static String get baseUrl => dotenv.env['BASE_URL']!;

  // Auth
  static const login          = '/auth/login/';
  static const refresh        = '/auth/refresh/';
  static const register       = '/auth/register/';
  static const me             = '/auth/me/';

  // Pigeons
  static const pigeons        = '/pigeons/';
  static const breeds         = '/pigeons/breeds/';
  static String pigeonDetail(int id) => '/pigeons/$id/';

  // Marketplace
  static const marketplace    = '/marketplace/';
  static String listingDetail(int id) => '/marketplace/$id/';

  // Pedigrees
  static String pedigree(int pigeonId)     => '/pedigree/$pigeonId/';
  static String pedigreeEdit(int pigeonId) => '/pedigree/$pigeonId/edit/';

  // Feed
  static const feedGenerate   = '/feed/generate/';

  // Messaging
  static const conversations  = '/messages/';
  static String conversation(int id) => '/messages/$id/';
  static String sendMessage(int id)  => '/messages/$id/send/';
}
```

### Dio Client with Auth Interceptor

```dart
// core/network/dio_client.dart
class DioClient {
  late final Dio _dio;
  final SecureStorage _storage;

  DioClient(this._storage) {
    _dio = Dio(BaseOptions(
      baseUrl: ApiConstants.baseUrl,
      connectTimeout: const Duration(seconds: 15),
      receiveTimeout: const Duration(seconds: 15),
    ));
    _dio.interceptors.add(_AuthInterceptor(_dio, _storage));
  }

  Dio get dio => _dio;
}
```

### Token Refresh Flow

On every 401 response:
1. Read refresh token from `SecureStorage`.
2. POST `/api/auth/refresh/` with `{"refresh": "..."}`.
3. Save new access token.
4. Retry the original request with the new token.
5. If refresh also fails → clear storage → navigate to `/login`.

---

## Data Models

All models use `freezed` + `json_serializable`. Key shapes:

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
  }) = _User;
  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
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
    required String gender,     // 'M', 'F', 'U'
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
    required String status,
    @JsonKey(name: 'is_negotiable') required bool isNegotiable,
    @JsonKey(name: 'views_count') required int viewsCount,
    required Pigeon pigeon,
    required int seller,
    @JsonKey(name: 'seller_name') String? sellerName,
    @JsonKey(name: 'created_at') required String createdAt,
  }) = _Listing;
  factory Listing.fromJson(Map<String, dynamic> json) => _$ListingFromJson(json);
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

@freezed
class FeedItem with _$FeedItem {
  factory FeedItem({
    required String grain,
    required String category,
    required int percentage,
    required double protein,
    required double fat,
    @JsonKey(name: 'grams_per_kg') required int gramsPerKg,
    @JsonKey(name: 'contrib_protein') required double contribProtein,
  }) = _FeedItem;
  factory FeedItem.fromJson(Map<String, dynamic> json) => _$FeedItemFromJson(json);
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

Each feature has an `AsyncNotifier` provider. Example pattern:

```dart
// features/pigeons/providers/pigeon_provider.dart

@riverpod
class PigeonList extends _$PigeonList {
  @override
  Future<List<Pigeon>> build() async {
    return ref.read(pigeonRepositoryProvider).getMyPigeons();
  }

  Future<void> addPigeon(Map<String, dynamic> data, File? image) async {
    await ref.read(pigeonRepositoryProvider).createPigeon(data, image);
    ref.invalidateSelf();  // refresh list
  }

  Future<void> deletePigeon(int id) async {
    await ref.read(pigeonRepositoryProvider).deletePigeon(id);
    ref.invalidateSelf();
  }
}

@riverpod
Future<Pigeon> pigeonDetail(PigeonDetailRef ref, int id) async {
  return ref.read(pigeonRepositoryProvider).getPigeon(id);
}
```

### Auth State

```dart
// features/auth/providers/auth_provider.dart

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
    String? location,
    double? minPrice,
    double? maxPrice,
    String? ordering,
  }) = _ListingFilter;
}

@riverpod
class MarketplaceNotifier extends _$MarketplaceNotifier {
  @override
  Future<List<Listing>> build() async {
    return ref.read(marketplaceRepositoryProvider)
              .getListings(ListingFilter());
  }

  Future<void> applyFilter(ListingFilter filter) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(
      () => ref.read(marketplaceRepositoryProvider).getListings(filter),
    );
  }
}
```

---

## Screen Descriptions

### SplashScreen
- Check token in `SecureStorage`
- If valid → navigate to `/home`
- If none → navigate to `/login`

### LoginScreen
- Username + password fields
- On submit: POST `/api/auth/login/` → save access + refresh tokens → navigate to `/home`
- Link to RegisterScreen

### RegisterScreen
- Username, email, first name, last name, location, password, confirm password
- On submit: POST `/api/auth/register/` → auto-login → navigate to `/home`

### ListingListScreen (Marketplace)
- Grid of `ListingCard` widgets (image + name + breed + price + location)
- Persistent filter bar: search field, breed dropdown, price range, location
- Tap card → `ListingDetailScreen`
- FAB (if authenticated) → `AddListingScreen`

### ListingDetailScreen
- Hero image carousel (pigeon images)
- Title, price, location, negotiable badge
- Seller info + "Message Seller" button → `ConversationScreen`
- Save/unsave toggle button
- Pigeon details section (breed, age, color, ring number)
- Pedigree link if available

### PigeonListScreen
- Grid of pigeon cards (primary image + name + breed + age)
- FAB → `PigeonFormScreen` (add)
- Tap card → `PigeonDetailScreen`

### PigeonDetailScreen
- Image carousel
- Full details: name, ring number, breed, gender, color, age, weight, description
- Action buttons: Edit, Delete, View Pedigree
- "List for Sale" shortcut → `AddListingScreen`

### PigeonFormScreen (Add / Edit)
- Fields: name, ring number, breed (dropdown), gender (radio), color (dropdown),
  date of birth (date picker), weight, description
- Image picker (camera or gallery) → primary image
- On submit: POST/PUT to pigeon API → navigate back

### PedigreeTreeScreen
- Visual tree widget showing pigeon → sire/dam → grandparents
- Each node: pigeon name + breed + ring number
- Nodes are tappable → navigate to that pigeon's detail
- "Edit Pedigree" button (only for owner)

### PedigreeEditScreen
- Searchable dropdown for Sire (filter: male pigeons owned by user or public)
- Searchable dropdown for Dam (filter: female pigeons)
- Notes field + is_public toggle
- On submit: POST `/api/pedigree/<id>/edit/`

### FeedGeneratorScreen
- Purpose selector (chips/segmented button): Racing / Breeding / Molting / Maintenance / Young
- Optional: target protein % slider (8–25)
- "Generate" button → GET `/api/feed/generate/`
- Results card:
  - Nutritional summary row (protein, fat, carbs, fiber, calories)
  - Grain table: grain name | category | % | g/kg | protein contrib
  - Colour-coded category badges (cereal/legume/seed)

### InboxScreen
- List of conversations ordered by last activity
- Each item: other user's name + last message preview + timestamp + unread dot
- Tap → `ConversationScreen`

### ConversationScreen
- Chat bubble UI (own messages right-aligned, other's left-aligned)
- Message input + send button
- Poll for new messages or use periodic refresh (30s)
- On enter: POST `/api/messages/<id>/send/`

### DashboardScreen
- Stats row: pigeon count, active listing count, unread message count
- Recent conversations list
- Quick links: My Pigeons, My Listings, Edit Profile

### ProfileEditScreen
- Fields: first name, last name, phone, location, bio
- Avatar picker (image_picker)
- PATCH `/api/auth/me/`

---

## Development Phases

### Phase 1 — Foundation
- [ ] Flutter project setup (`flutter create bph_app`)
- [ ] Add all dependencies to `pubspec.yaml`
- [ ] Configure `.env` with backend base URL
- [ ] Implement `DioClient` with auth interceptor and token refresh logic
- [ ] Implement `SecureStorage` wrapper for access/refresh tokens
- [ ] Set up `GoRouter` with all routes and auth redirect guard
- [ ] Build `MainShell` (bottom navigation scaffold)
- [ ] Run `build_runner` code generation

### Phase 2 — Authentication
- [ ] `User` model (freezed)
- [ ] `AuthRepository` (login, register, getMe, updateProfile)
- [ ] `AuthNotifier` provider
- [ ] `SplashScreen`
- [ ] `LoginScreen`
- [ ] `RegisterScreen`
- [ ] `ProfileEditScreen`

### Phase 3 — Pigeons
- [ ] `Pigeon`, `Breed`, `PigeonImage` models
- [ ] `PigeonRepository` (CRUD + image upload via multipart)
- [ ] `PigeonListNotifier`, `pigeonDetail` providers
- [ ] `PigeonListScreen`
- [ ] `PigeonDetailScreen`
- [ ] `PigeonFormScreen` (add + edit)

### Phase 4 — Marketplace
- [ ] `Listing` model
- [ ] `MarketplaceRepository` (list with filters, detail, create)
- [ ] `MarketplaceNotifier` with `ListingFilter`
- [ ] `ListingListScreen` with filter bar
- [ ] `ListingDetailScreen`
- [ ] `AddListingScreen`
- [ ] `MyListingsScreen`

### Phase 5 — Pedigrees
- [ ] `PedigreeRecord` model
- [ ] `PedigreeRepository`
- [ ] `PedigreeTreeScreen` (custom tree widget)
- [ ] `PedigreeEditScreen`

### Phase 6 — Feed Generator
- [ ] `FeedResult`, `FeedItem` models
- [ ] `FeedRepository`
- [ ] `FeedGeneratorScreen` with purpose chips + results table

### Phase 7 — Messaging
- [ ] `Conversation`, `Message` models
- [ ] `MessagingRepository`
- [ ] `InboxScreen`
- [ ] `ConversationScreen` with periodic refresh

### Phase 8 — Dashboard & Polish
- [ ] `DashboardScreen`
- [ ] `DashboardRepository`
- [ ] Loading skeletons for all list screens
- [ ] Empty state widgets
- [ ] Error handling UI (retry buttons)
- [ ] Pull-to-refresh on all list screens
- [ ] App icon + splash image
- [ ] Android build configuration (`AndroidManifest.xml` internet permission)

---

## Running the App

```bash
# Install dependencies
flutter pub get

# Generate freezed/json models and riverpod providers
dart run build_runner build --delete-conflicting-outputs

# Run on connected device or emulator
flutter run

# Build APK
flutter build apk --release

# Build AAB for Play Store
flutter build appbundle --release
```

### Android Manifest Requirements

Add to `android/app/src/main/AndroidManifest.xml`:

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />
<uses-permission android:name="android.permission.CAMERA" />
```

### Connecting to Local Dev Server

| Device | Base URL |
|---|---|
| Android Emulator | `http://10.0.2.2:8000/api` |
| Physical Device (USB) | `http://<your-LAN-IP>:8000/api` |
| iOS Simulator | `http://localhost:8000/api` |

Ensure Django is running with:

```bash
python manage.py runserver 0.0.0.0:8000
```

---

## Notes for Backend Coordination

- **Image upload:** Pigeon images are uploaded as `multipart/form-data`. The `PigeonImage` endpoint is separate from `Pigeon` — image upload should be done as a second POST after the pigeon is created. A dedicated `/api/pigeons/<id>/images/` endpoint may need to be added to the backend.
- **Conversation start:** There is no `/api/messages/start/<listing_id>/` endpoint yet — a `POST /api/messages/start/` endpoint with `listing_id` and `seller_id` in the body should be added to the backend for the "Message Seller" flow.
- **Saved listings:** There is no API endpoint for saving/unsaving listings — a `POST /api/marketplace/<id>/save/` endpoint should be added.
- **Pagination:** All list endpoints return paginated results (`count`, `next`, `previous`, `results`). Implement infinite scroll or "Load More" using the `next` URL.
- **CORS:** Already set to `CORS_ALLOW_ALL_ORIGINS = True` in development — fine for local testing.

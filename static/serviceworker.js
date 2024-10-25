var CACHE_NAME = 'That Vacation-v2';
var urlsToCache = [
    '/',
    '/static/img/logo.jpg',
    'static/lib/animate/animate.min.css',
    'static/lib/owlcarousel/assets/owl.carousel.min.css',
    'static/lib/tempusdominus/css/tempusdominus-bootstrap-4.min.css',
    'static/css/style.css',
    'static/css/bootstrap.min.css',
];

self.addEventListener('install', function(event) {

    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                console.log('Opened cache');
                return cache.addAll(urlsToCache);
            })
    );
});

self.addEventListener('fetch', function(event) {
    event.respondWith(
        fetch(event.request)
        .then(function(result){
            return caches.open(CACHE_NAME)
            .then(function(c){
                c.put(event.request.url, result.clone());
                return result;
            })
        })
        .catch(function(e){
            return caches.match(event.request)
        })
    );
});
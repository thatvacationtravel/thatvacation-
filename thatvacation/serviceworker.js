var CACHE_NAME = 'That vacation-cache-v1';
var urlsToCache = [
    '/',

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



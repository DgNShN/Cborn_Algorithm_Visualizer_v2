ALGORITHM_OVERVIEWS = {
    "Bubble Sort": {
        "overview": "Bubble Sort, yan yana duran elemanları karşılaştırır. Soldaki eleman sağdakinden büyükse yer değiştirir. Her turun sonunda en büyük kalan eleman sağ tarafa oturur.",
        "why": "Bu algoritma basit ama verimsizdir. Küçük veri setlerinde öğretim amaçlı çok uygundur çünkü her karşılaştırma ve swap net biçimde görülebilir.",
    },
    "Selection Sort": {
        "overview": "Selection Sort, her turda sıralanmamış bölümdeki en küçük elemanı bulur ve başa koyar.",
        "why": "Bu algoritma minimum elemanı seçme mantığını öğretir. Swap sayısı genelde düşüktür ama karşılaştırma sayısı yüksektir.",
    },
    "Insertion Sort": {
        "overview": "Insertion Sort, her yeni elemanı soldaki sıralı bölümün doğru yerine yerleştirir.",
        "why": "Neredeyse sıralı dizilerde çok verimli olabilir. Gerçek hayatta kart dizer gibi çalıştığı için sezgisel olarak anlaşılması kolaydır.",
    },
    "Merge Sort": {
        "overview": "Merge Sort, diziyi sürekli ikiye böler, küçük parçaları sıralar ve sonra birleştirir.",
        "why": "Böl ve fethet yaklaşımını öğretir. Büyük veri setlerinde daha verimlidir ve zaman karmaşıklığı daha stabildir.",
    },
    "Quick Sort": {
        "overview": "Quick Sort, bir pivot seçer ve elemanları pivotun küçükleri sola, büyükleri sağa gelecek şekilde böler.",
        "why": "Pratikte çok güçlüdür. Pivot seçimi ve parçalama mantığını anlamak algoritma bilgisini ciddi seviyede yükseltir.",
    },
    "Linear Search": {
        "overview": "Linear Search, hedef değeri bulmak için elemanları baştan sona tek tek kontrol eder.",
        "why": "En basit arama yöntemidir. Veri sıralı olmak zorunda değildir ama büyük listelerde yavaş kalabilir.",
    },
    "Binary Search": {
        "overview": "Binary Search, sıralı veri üzerinde ortadaki elemanı kontrol eder ve arama alanını yarıya indirir.",
        "why": "Arama uzayını azaltma fikrini öğretir. Sıralı veri üzerinde çok hızlı çalışır.",
    },
}


def get_algorithm_overview(algorithm_name):
    info = ALGORITHM_OVERVIEWS.get(algorithm_name, {})
    return {
        "overview": info.get("overview", "Bu algoritma için genel açıklama bulunamadı."),
        "why": info.get("why", "Bu algoritmanın öğretici notu bulunamadı."),
    }


def build_step_explanation(algorithm_name, step):
    message = step.get("message", "")
    variables = step.get("variables", {})
    active = step.get("active", [])
    swap = step.get("swap", [])
    found = step.get("found_indices", [])
    sorted_indices = step.get("sorted_indices", [])

    if algorithm_name == "Bubble Sort":
        return explain_bubble_sort(message, variables, active, swap, sorted_indices)

    if algorithm_name == "Selection Sort":
        return explain_selection_sort(message, variables, active, swap, sorted_indices)

    if algorithm_name == "Insertion Sort":
        return explain_insertion_sort(message, variables, active, swap, sorted_indices)

    if algorithm_name == "Merge Sort":
        return explain_merge_sort(message, variables, active, swap, sorted_indices)

    if algorithm_name == "Quick Sort":
        return explain_quick_sort(message, variables, active, swap, sorted_indices)

    if algorithm_name == "Linear Search":
        return explain_linear_search(message, variables, active, found)

    if algorithm_name == "Binary Search":
        return explain_binary_search(message, variables, active, found)

    return {
        "title": "Step Explanation",
        "explanation": message or "Bu adım için açıklama yok.",
        "why": "Algoritma şu anda bir işlem gerçekleştiriyor.",
    }


def explain_bubble_sort(message, variables, active, swap, sorted_indices):
    if swap:
        return {
            "title": "Swap Yapıldı",
            "explanation": "Yan yana iki eleman karşılaştırıldı ve soldaki daha büyük olduğu için yer değiştirildi. Bubble Sort büyük değerleri sağa doğru iter.",
            "why": "Bu hareket sayesinde her turun sonunda en büyük kalan eleman dizinin sonuna yaklaşır.",
        }
    if "Comparing" in message:
        return {
            "title": "Karşılaştırma",
            "explanation": "Bubble Sort şu anda komşu iki elemanı karşılaştırıyor. Amaç sıralama kuralını bozup bozmadıklarını görmek.",
            "why": "Eğer soldaki büyükse swap yapılır; değilse sıra korunur.",
        }
    if sorted_indices:
        return {
            "title": "Bir Eleman Yerine Oturdu",
            "explanation": "Bu turun sonunda en az bir eleman doğru konumuna oturdu.",
            "why": "Bubble Sort her turda sağ tarafta sıralı bölgeyi büyütür.",
        }
    return {
        "title": "Bubble Sort Adımı",
        "explanation": message or "Bubble Sort bir işlem yapıyor.",
        "why": "Algoritma komşu karşılaştırmalarla sıralamayı tamamlamaya çalışıyor.",
    }


def explain_selection_sort(message, variables, active, swap, sorted_indices):
    if "New minimum" in message:
        return {
            "title": "Yeni Minimum Bulundu",
            "explanation": "Algoritma, şu ana kadar gördüğü en küçük elemandan daha küçük bir değer buldu.",
            "why": "Selection Sort her turda minimum elemanı seçip başa taşır.",
        }
    if swap:
        return {
            "title": "Minimum Başa Alındı",
            "explanation": "Bulunan en küçük eleman, sıralanmamış bölümün başındaki elemanla yer değiştirdi.",
            "why": "Bu işlemle dizinin sol tarafı adım adım sıralı hale gelir.",
        }
    if "Checking" in message:
        return {
            "title": "Minimum Aranıyor",
            "explanation": "Selection Sort şu anda sıralanmamış bölümde en küçük elemanı arıyor.",
            "why": "Minimum bulunmadan doğru elemanı başa yerleştiremez.",
        }
    return {
        "title": "Selection Sort Adımı",
        "explanation": message or "Selection Sort bir işlem yapıyor.",
        "why": "Algoritma her turda doğru elemanı seçmeye çalışıyor.",
    }


def explain_insertion_sort(message, variables, active, swap, sorted_indices):
    if "Trying to insert" in message:
        key = variables.get("key")
        return {
            "title": "Yeni Eleman Yerleştirilecek",
            "explanation": f"Şu anda {key} değeri, soldaki sıralı bölüm içinde doğru yere yerleştirilmeye çalışılıyor.",
            "why": "Insertion Sort diziyi soldan sağa büyüyen sıralı bir alan gibi işler.",
        }
    if "Comparing" in message:
        return {
            "title": "Yer Kontrolü",
            "explanation": "Algoritma, anahtar elemanın soldaki elemanlardan küçük olup olmadığını kontrol ediyor.",
            "why": "Küçükse sola kaymalı, büyükse bulunduğu yere yerleşmelidir.",
        }
    if swap:
        return {
            "title": "Kaydırma Yapıldı",
            "explanation": "Daha büyük bir eleman sağa kaydırıldı, böylece anahtar eleman için boş yer açıldı.",
            "why": "Insertion Sort gerçek yerleştirmeyi yapmadan önce gerekli boşluğu oluşturur.",
        }
    if "Inserted key" in message:
        return {
            "title": "Eleman Yerine Yerleşti",
            "explanation": "Anahtar eleman sıralı bölüm içindeki doğru konuma yerleştirildi.",
            "why": "Bu adımla sıralı bölüm bir eleman daha büyür.",
        }
    return {
        "title": "Insertion Sort Adımı",
        "explanation": message or "Insertion Sort bir işlem yapıyor.",
        "why": "Algoritma elemanları doğru sıraya sokuyor.",
    }


def explain_merge_sort(message, variables, active, swap, sorted_indices):
    if "Splitting range" in message:
        left = variables.get("left")
        right = variables.get("right")
        mid = variables.get("mid")
        return {
            "title": "Dizi Bölünüyor",
            "explanation": f"Algoritma {left}-{right} aralığını iki parçaya ayırıyor. Orta nokta {mid}.",
            "why": "Merge Sort önce problemi küçültür, sonra parçaları sıralayıp birleştirir.",
        }
    if "Comparing left" in message:
        return {
            "title": "İki Parça Karşılaştırılıyor",
            "explanation": "Birleştirme aşamasında sol ve sağ alt dizilerin başındaki elemanlar karşılaştırılıyor.",
            "why": "Küçük olan sonuç dizisine eklenir; böylece birleşen bölüm sıralı kalır.",
        }
    if "Writing merged value" in message:
        return {
            "title": "Birleşmiş Değer Yazılıyor",
            "explanation": "Karşılaştırma sonucu seçilen değer ana diziye geri yazılıyor.",
            "why": "Bu adım sıralı parçaları tek bir sıralı parçada birleştirir.",
        }
    if "Merged range" in message:
        return {
            "title": "Bir Bölüm Tamamlandı",
            "explanation": "Seçilen aralık başarıyla birleştirildi ve sıralı hale geldi.",
            "why": "Merge Sort, küçük sıralı parçaları büyüterek tüm diziyi sıralar.",
        }
    return {
        "title": "Merge Sort Adımı",
        "explanation": message or "Merge Sort bir işlem yapıyor.",
        "why": "Algoritma bölme ve birleştirme stratejisiyle ilerliyor.",
    }


def explain_quick_sort(message, variables, active, swap, sorted_indices):
    if "Pivot selected" in message:
        pivot = variables.get("pivot")
        pivot_index = variables.get("pivot_index")
        return {
            "title": "Pivot Seçildi",
            "explanation": f"Pivot olarak {pivot_index}. indisteki {pivot} değeri seçildi.",
            "why": "Quick Sort diğer elemanları pivota göre iki tarafa ayırır.",
        }
    if "Comparing arr" in message:
        return {
            "title": "Pivot ile Karşılaştırma",
            "explanation": "Şu anki eleman pivot ile kıyaslanıyor. Küçükse sol bölgeye alınacak.",
            "why": "Bu karşılaştırmalar diziyi iki parçaya ayırmanın temelidir.",
        }
    if swap and "Placed pivot" not in message:
        return {
            "title": "Bölme İçin Swap",
            "explanation": "Pivotdan küçük bir eleman doğru bölgeye taşındı.",
            "why": "Bu işlem pivotun sol tarafında küçük elemanlar, sağ tarafında büyük elemanlar oluşmasını sağlar.",
        }
    if "Placed pivot" in message:
        return {
            "title": "Pivot Yerine Oturdu",
            "explanation": "Pivot artık doğru konumuna yerleşti.",
            "why": "Bundan sonra pivotun sol ve sağ tarafları ayrı ayrı sıralanır.",
        }
    return {
        "title": "Quick Sort Adımı",
        "explanation": message or "Quick Sort bir işlem yapıyor.",
        "why": "Algoritma pivot etrafında parçalama yapıyor.",
    }


def explain_linear_search(message, variables, active, found):
    if found:
        target = variables.get("target")
        i = variables.get("i")
        return {
            "title": "Hedef Bulundu",
            "explanation": f"Aranan değer {target}, {i}. indiste bulundu.",
            "why": "Linear Search, diziyi tek tek gezdiği için bulduğu anda işlemi bitirir.",
        }
    if "Checking index" in message:
        return {
            "title": "Eleman Kontrol Ediliyor",
            "explanation": "Linear Search, sıradaki elemanı hedef değerle karşılaştırıyor.",
            "why": "Bu yöntem veri sıralı olmasa bile çalışır, ama her elemanı tek tek inceleyebilir.",
        }
    if "not found" in message.lower():
        return {
            "title": "Hedef Bulunamadı",
            "explanation": "Tüm elemanlar kontrol edildi ama hedef değer bulunamadı.",
            "why": "Linear Search en kötü durumda listenin tamamını tarar.",
        }
    return {
        "title": "Linear Search Adımı",
        "explanation": message or "Linear Search bir işlem yapıyor.",
        "why": "Algoritma hedef değeri satır satır arıyor.",
    }


def explain_binary_search(message, variables, active, found):
    if "sorted automatically" in message.lower():
        return {
            "title": "Sıralı Veri Gerekiyor",
            "explanation": "Binary Search yalnızca sıralı veri üzerinde çalışır. Bu yüzden veri önce sıralandı.",
            "why": "Orta elemanı kontrol edip alanı yarıya indirme mantığı ancak sıralı dizide anlamlıdır.",
        }
    if "Checking middle index" in message:
        mid = variables.get("mid")
        value = variables.get("value")
        return {
            "title": "Orta Nokta Kontrolü",
            "explanation": f"Şu anda orta nokta olarak {mid}. indis seçildi ve değeri {value} kontrol ediliyor.",
            "why": "Binary Search her adımda arama alanını yarıya indirmeye çalışır.",
        }
    if found:
        target = variables.get("target")
        mid = variables.get("mid")
        return {
            "title": "Hedef Bulundu",
            "explanation": f"Aranan değer {target}, orta noktada bulundu: indeks {mid}.",
            "why": "Binary Search doğru tahmine ulaştığında çok az adımda sonuca gider.",
        }
    if "moving right" in message.lower():
        return {
            "title": "Sağa Gidiliyor",
            "explanation": "Hedef değer ortadaki değerden büyük olduğu için sol yarı elendi ve sağ yarıya geçildi.",
            "why": "Bu, Binary Search’ün gücüdür: alanın yarısını tek adımda çöpe atar.",
        }
    if "moving left" in message.lower():
        return {
            "title": "Sola Gidiliyor",
            "explanation": "Hedef değer ortadaki değerden küçük olduğu için sağ yarı elendi ve sol yarıya geçildi.",
            "why": "Her adımda arama alanı küçülür ve çözüm hızlanır.",
        }
    if "not found" in message.lower():
        return {
            "title": "Hedef Bulunamadı",
            "explanation": "Arama alanı tükendi ve hedef değer bulunamadı.",
            "why": "Bu, hedefin dizide olmadığını gösterir.",
        }
    return {
        "title": "Binary Search Adımı",
        "explanation": message or "Binary Search bir işlem yapıyor.",
        "why": "Algoritma sıralı dizide alanı yarıya indirerek arama yapıyor.",
    }
# Food-101 Dataset

## Overview

Food-101 is a large food image dataset containing:
- **101 food categories**
- **1,000 images per class** (750 training, 250 test)
- **101,000 images total**
- Approximately **5 GB** uncompressed

Published by: Bossard, Lukas, Matthieu Guillaumin, and Luc Van Gool.  
Original paper: *Food-101 – Mining Discriminative Components with Random Forests* (ECCV 2014)

---

## Download Instructions

### Option 1: Official Website (Recommended)

```bash
# Create the dataset directory
mkdir -p ml/dataset/food-101

# Download from official source (~4.6 GB)
wget http://data.vision.ee.ethz.ch/cvl/food-101.tar.gz -P ml/dataset/

# Extract
tar -xzf ml/dataset/food-101.tar.gz -C ml/dataset/

# Verify extraction — you should see 101 folders
ls ml/dataset/food-101/images/ | wc -l
# Expected output: 101
```

### Option 2: Kaggle (Alternative)

```bash
# Install Kaggle CLI first: pip install kaggle
# Set up your Kaggle API key: ~/.kaggle/kaggle.json

kaggle datasets download -d kmader/food41 -p ml/dataset/
unzip ml/dataset/food41.zip -d ml/dataset/food-101/
```

### Option 3: TensorFlow Datasets (For Notebooks)

```python
import tensorflow_datasets as tfds

# This downloads and manages the dataset automatically
dataset, info = tfds.load('food101', with_info=True, as_supervised=True)
```

---

## Expected Folder Structure After Download

```
ml/dataset/food-101/
├── images/
│   ├── apple_pie/
│   │   ├── 1005649.jpg
│   │   ├── 1011328.jpg
│   │   └── ... (1000 images total)
│   ├── baby_back_ribs/
│   ├── baklava/
│   ├── ...
│   └── waffles/
├── meta/
│   ├── classes.txt          ← List of all 101 class names
│   ├── labels.txt
│   ├── test.txt             ← Test image paths
│   ├── train.txt            ← Train image paths
│   └── train.json
└── license_agreement.txt
```

---

## Dataset Statistics

| Split | Images | Per Class |
|-------|--------|-----------|
| Train | 75,750 | 750 |
| Test  | 25,250 | 250 |
| **Total** | **101,000** | **1,000** |

---

## Disk Space Requirements

| Stage | Space |
|-------|-------|
| Compressed archive | ~4.6 GB |
| Extracted dataset | ~5.1 GB |
| Preprocessed tensors (if cached) | ~8–12 GB |

**Recommendation**: Keep the dataset on a drive with at least 20 GB free.

---

## The 101 Food Classes

```
apple_pie, baby_back_ribs, baklava, beef_carpaccio, beef_tartare,
beet_salad, beignets, bibimbap, bread_pudding, breakfast_burrito,
bruschetta, caesar_salad, cannoli, caprese_salad, carrot_cake,
ceviche, cheesecake, cheese_plate, chicken_curry, chicken_quesadilla,
chicken_wings, chocolate_cake, chocolate_mousse, churros, clam_chowder,
club_sandwich, crab_cakes, creme_brulee, croque_madame, cup_cakes,
deviled_eggs, donuts, dumplings, edamame, eggs_benedict, escargots,
falafel, filet_mignon, fish_and_chips, foie_gras, french_fries,
french_onion_soup, french_toast, fried_calamari, fried_rice,
frozen_yogurt, garlic_bread, gnocchi, greek_salad, grilled_cheese_sandwich,
grilled_salmon, guacamole, gyoza, hamburger, hot_and_sour_soup, hot_dog,
huevos_rancheros, hummus, ice_cream, lasagna, lobster_bisque,
lobster_roll_sandwich, macaroni_and_cheese, macarons, miso_soup, mussels,
nachos, omelette, onion_rings, oysters, pad_thai, paella, pancakes,
panna_cotta, peking_duck, pho, pizza, pork_chop, poutine, prime_rib,
pulled_pork_sandwich, ramen, ravioli, red_velvet_cake, risotto, samosa,
sashimi, scallops, seaweed_salad, shrimp_and_grits, spaghetti_bolognese,
spaghetti_carbonara, spring_rolls, steak, strawberry_shortcake, sushi,
tacos, takoyaki, tiramisu, tuna_tartare, waffles
```

---

## Notes

- Images vary significantly in quality, angle, and lighting — this is intentional for robustness.
- Some images are mislabelled in the original dataset (~20% noise in training set).
- The test set is manually reviewed and considered high quality.
- The `.gitignore` is set to exclude the `food-101/` folder from version control.

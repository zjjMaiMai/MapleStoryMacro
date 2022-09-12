import cv2

MM_TL_TEMPLATE = cv2.imread("template/minimap_tl.png", cv2.IMREAD_COLOR)
MM_BR_TEMPLATE = cv2.imread("template/minimap_br.png", cv2.IMREAD_COLOR)
PLAYER_TEMPLATE = cv2.imread("template/player.png", cv2.IMREAD_COLOR)
RUNE_TEMPLATE = cv2.imread("template/rune.png", cv2.IMREAD_COLOR)
RUNE_DEBUFF_TEMPLATE = cv2.imread("template/rune_debuff.png", cv2.IMREAD_COLOR)
MUSHROOMS_TEMPLATE = cv2.imread("template/mushrooms.png", cv2.IMREAD_COLOR)


def split_image(image, bbox):
    return image[bbox[1] : bbox[3], bbox[0] : bbox[2]]


def template_matching(image, template, threshold):
    result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    _, c, _, tl = cv2.minMaxLoc(result)
    if c < threshold:
        return None
    h, w, _ = template.shape
    return [tl[0], tl[1], tl[0] + w, tl[1] + h]


def minimap_detect(image, threshold=0.8):
    image_tl = image[:384, :384]
    tl = template_matching(image_tl, MM_TL_TEMPLATE, threshold)
    if tl is None:
        return None

    br = template_matching(image_tl, MM_BR_TEMPLATE, threshold)
    if br is None:
        return None

    if tl[0] >= br[2] or tl[1] >= br[3]:
        return None

    return [tl[0], tl[1], br[2], br[3]]


def player_detect(image, threshold=0.8):
    return template_matching(image, PLAYER_TEMPLATE, threshold)


def rune_detect(image, threshold=0.8):
    pos = template_matching(image, RUNE_TEMPLATE, threshold)
    if pos is None:
        return None

    debuff = template_matching(image, RUNE_DEBUFF_TEMPLATE, threshold)
    if debuff is not None:
        return None

    return pos


def mushrooms_detect(image, threshold=0.8):
    return template_matching(image, MUSHROOMS_TEMPLATE, threshold)


if __name__ == "__main__":
    from window import find_window, capture

    while True:
        image = capture(find_window("MapleStory"))
        if image is None:
            continue

        minimap = minimap_detect(image)
        if minimap is None:
            continue

        minimap = split_image(image, minimap)
        print(player_detect(minimap), rune_detect(minimap))
        cv2.imshow("Minimap", minimap)
        cv2.waitKey(1)

import cv2

MM_TL_TEMPLATE = cv2.imread("template/minimap_tl.png", cv2.IMREAD_COLOR)
MM_BR_TEMPLATE = cv2.imread("template/minimap_br.png", cv2.IMREAD_COLOR)
PLAYER_TEMPLATE = cv2.imread("template/player.png", cv2.IMREAD_COLOR)
RUNE_TEMPLATE = cv2.imread("template/rune.png", cv2.IMREAD_COLOR)
RUNE_DEBUFF_TEMPLATE = cv2.imread("template/rune_debuff.png", cv2.IMREAD_COLOR)
MUSHROOMS_TEMPLATE = cv2.imread("template/mushrooms.png", cv2.IMREAD_COLOR)


def split_image(image, bbox):
    return image[bbox[1] : bbox[3], bbox[0] : bbox[2]]


def _template_matching(image, template, threshold):
    result = cv2.matchTemplate(image, template, cv2.TM_CCORR_NORMED)
    _, c, _, tl = cv2.minMaxLoc(result)
    if c < threshold:
        return None
    h, w, _ = template.shape
    return [tl[0], tl[1], tl[0] + w, tl[1] + h]


def template_matching(image, template, threshold, last=None, r=5):
    if last is not None:
        h, w = image.shape[:2]
        p = [
            max(last[0] - r, 0),
            max(last[1] - r, 0),
            min(last[2] + r, w),
            min(last[3] + r, h),
        ]
        pi = split_image(image, p)
        pr = _template_matching(pi, template, threshold)
        if pr is not None:
            return [
                pr[0] + p[0],
                pr[1] + p[1],
                pr[2] + p[0],
                pr[3] + p[1],
            ]
    return _template_matching(image, template, threshold)


def minimap_detect(image, threshold=0.8, last=None, r=5):
    if last is not None:
        h, w = MM_TL_TEMPLATE.shape[:2]
        tl_last = [last[0], last[1], last[0] + w, last[1] + h]
        bl_last = [last[2] - w, last[3] - h, last[2], last[3]]
    else:
        tl_last = None
        bl_last = None

    tl = template_matching(image, MM_TL_TEMPLATE, threshold, tl_last, r)
    if tl is None:
        return None

    br = template_matching(image, MM_BR_TEMPLATE, threshold, bl_last, r)
    if br is None:
        return None

    if tl[0] >= br[2] or tl[1] >= br[3]:
        return None

    return [tl[0], tl[1], br[2], br[3]]


def player_detect(image, threshold=0.8, last=None, r=5):
    return template_matching(image, PLAYER_TEMPLATE, threshold, last, r)


def rune_detect(image, threshold=0.8, last=None, r=5):
    return template_matching(image, RUNE_TEMPLATE, threshold, last, r)


def rune_debuff_detect(image, threshold=0.8):
    image_buff = image[55:74]
    rel_pos = template_matching(image_buff, RUNE_DEBUFF_TEMPLATE, threshold)
    if rel_pos is not None:
        return [rel_pos[0], rel_pos[1] + 55, rel_pos[2], rel_pos[3] + 55]
    return None


def mushrooms_detect(image, threshold=0.8):
    image_buff = image[55:74]
    rel_pos = template_matching(image_buff, MUSHROOMS_TEMPLATE, threshold)
    if rel_pos is not None:
        return [rel_pos[0], rel_pos[1] + 55, rel_pos[2], rel_pos[3] + 55]
    return None


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

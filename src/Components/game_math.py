


def is_in_screen_rect(top_left, bottom_right, point):
    return top_left.x < point.x < bottom_right.x and top_left.y < point.y < bottom_right.y


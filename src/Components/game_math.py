


def is_in_screen_rect(top_left, bottom_right, point):
    return top_left.x < point.x < bottom_right.x and top_left.y < point.y < bottom_right.y



def is_overlapping_rect(rect1, rect2):
    return all(d > 0 for d in (
        rect1.position.x + rect1.half_size.x - (rect2.position.x - rect2.half_size.x),
        rect2.position.x + rect2.half_size.x - (rect1.position.x - rect1.half_size.x),
        rect1.position.y + rect1.half_size.y - (rect2.position.y - rect2.half_size.y),
        rect2.position.y + rect2.half_size.y - (rect1.position.y - rect1.half_size.y)
    ))


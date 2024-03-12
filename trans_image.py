import os
import cv2


"""
用滑窗的方式将图像切割为子图，并转换标注位置生成新的标签。

"""
def read_yolo_label(label_path):
    with open(label_path, 'r') as file:
        lines = file.readlines()
    objects = []
    for line in lines:
        data = line.strip().split()
        if len(data) == 5:
            class_id = int(data[0])
            x_center = float(data[1])
            y_center = float(data[2])
            width = float(data[3])
            height = float(data[4])
            objects.append((class_id, x_center, y_center, width, height))
    return objects

def write_yolo_label(label_path, objects):
    with open(label_path, 'w') as file:
        for obj in objects:
            class_id, x_center, y_center, width, height = obj
            line = f"{class_id} {x_center} {y_center} {width} {height}\n"
            file.write(line)


            
def sliding_window(image_path, label_path, output_dir, window_size):
    image = cv2.imread(image_path)
    h, w = image.shape[:2]
    if label_path:
        objects = read_yolo_label(label_path)

    step_size = int(window_size)

    for y in range(0, h - window_size + 1, step_size):
        for x in range(0, w - window_size + 1, step_size):
            subimage = image[y:y+window_size, x:x+window_size]
            subimage_name = f"{os.path.splitext(os.path.basename(image_path))[0]}_{y}_{x}.jpg"
            cv2.imwrite(os.path.join(output_dir, subimage_name), subimage)
            if label_path:
            # 换算子图中的标签
                subimage_objects = []
                for obj in objects:
                    class_id, x_center, y_center, width, height = obj
                    x_min = int((x_center - width / 2) * w)
                    y_min = int((y_center - height / 2) * h)
                    x_max = int((x_center + width / 2) * w)
                    y_max = int((y_center + height / 2) * h)

                    if x_min >= x and x_max <= x + window_size and \
                    y_min >= y and y_max <= y + window_size:
                        x_center = (x_center * w - x) / window_size
                        y_center =  (y_center * h - y) / window_size
                        width = width * w / window_size
                        height = height * h / window_size
                        subimage_objects.append((class_id, x_center, y_center, width, height))
                if subimage_objects:
                    subimage_label_path = os.path.join(output_dir, f"{os.path.splitext(subimage_name)[0]}.txt")
                    write_yolo_label(subimage_label_path, subimage_objects)


def crop_all_files(folder_path, output_dir, window_size):
    jpg_files = [f for f in os.listdir(folder_path) if f.endswith(".jpg")]
    for jpg_file in jpg_files:
        jpg_file_name, _ = os.path.splitext(jpg_file)
        label_file = jpg_file_name + ".txt"
        if label_file in os.listdir(folder_path):
            # print(f"{jpg_file} 对应的 txt 文件存在")
            pass
            # sliding_window(os.path.join(folder_path, jpg_file), os.path.join(folder_path,label_file), output_dir, window_size)
        else:
            # print(f"{jpg_file} 对应的 txt 文件不存在")
            sliding_window(os.path.join(folder_path,jpg_file), None, output_dir, window_size)
            
# 示例使用方法
if __name__ == "__main__":
    imgfolder_pth = r"E:\Desktop\CVproj\DefectDetection\data\2024-01-04-fanguang"
    output_dir = r"E:\Desktop\CVproj\DefectDetection\data\background"
    window_size = 640  # 滑窗的尺寸
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    crop_all_files(imgfolder_pth, output_dir, window_size)

from PIL import Image
import numpy as np
from sys import exit


class Thresold:
    def sobel(self, mat):
        operator = [[1, 2, 1],
                    [0, 0, 0],
                    [-1, -2, -1]]
        sobel_out = 0
        for i in range(3):
            for j in range(3):
                sobel_out += (mat[i][j] * operator[i][j])

        return sobel_out

    def laplasian(self, mat):
        operator = [[0, 0, 0], [1, -4, 1], [0, 1, 0]]
        laplasian_out = 0
        for i in range(3):
            for j in range(3):
                laplasian_out += (mat[i][j] * operator[i][j])

        return laplasian_out

    def curvature(self, sobel, lap):
        c = (sobel ** 2) ** 1.5
        return lap / (1 + c)

    def thresold(self, matrix):
        curvature_matrix = []
        for i in range(len(matrix)-2):
            for j in range(len(matrix[i])-2):
                m, l = [], i
                for k in range(3):
                    # if j + 2 < 9:
                    m.append([matrix[l][j], matrix[l][j + 1], matrix[l][j + 2]])
                    l += 1
                # print(m)
                sob = self.sobel(m)
                lap = self.laplasian(m)
                curv = self.curvature(sob, lap)
                curvature_matrix.append(curv)

        thr = sum(curvature_matrix) / len(curvature_matrix)
        return thr, curvature_matrix

    def rgb_sum(self, image_arr):
        image_list = []
        for i in range(len(image_arr)):
            l = []
            for j in range(len(image_arr[i])):
                l.append(sum(image_arr[i][j]))
            image_list.append(l)
        return self.thresold(image_list)


class Message:
    def __fillMSB(self, inp):
        inp = inp.split("b")[-1]
        inp = '0'*(7-len(inp))+inp
        return [int(x) for x in inp]

    def __decrypt_pixels(self, pixels):
        pixels = [str(x % 2) for x in pixels]
        bin_repr = "".join(pixels)
        return chr(int(bin_repr, 2))

    def encode(self, image_path, msg, target_path=""):
        image = Image.open(image_path)
        img = np.array(image)
        imgArr = img.flatten()
        msg += "<-END->"
        msgArr = [self.__fillMSB(bin(ord(ch))) for ch in msg]

        th = Thresold()
        thresold, curvature_matrix = th.rgb_sum(img)

        idx = 0
        for i, j in enumerate(curvature_matrix):
            if j > thresold:
                idx = i * 3
                break

        for char in msgArr:
            for bit in char:
                if bit == 1:
                    if imgArr[idx] == 0:
                        imgArr[idx] = 1
                    else:
                        imgArr[idx] = imgArr[idx] if imgArr[idx] % 2 == 1 else imgArr[idx]-1
                else:
                    if imgArr[idx] == 255:
                        imgArr[idx] = 254
                    else:
                        imgArr[idx] = imgArr[idx] if imgArr[idx] % 2 == 0 else imgArr[idx]+1
                idx += 1

        savePath = target_path + image_path.split(".")[0] + "_encrypted.png"

        resImg = Image.fromarray(np.reshape(imgArr, img.shape))
        resImg.save(savePath)
        return

    def decode(self, image_path, target_path=""):
        original_image_path = input("Enter the path of the original Image: ")
        image = np.array(Image.open(original_image_path))
        th = Thresold()
        thresold, curvature_matrix = th.rgb_sum(image)

        idx = 0
        for i, j in enumerate(curvature_matrix):
            if j > thresold:
                idx = i * 3
                break

        img = np.array(Image.open(image_path))
        imgArr = np.array(img).flatten()

        decrypted_message = ""
        for i in range(idx, len(imgArr), 7):
            decrypted_char = self.__decrypt_pixels(imgArr[i:i+7])
            decrypted_message += decrypted_char

            if decrypted_message.endswith("<-END->"):
                break

        return decrypted_message[:-7]


if __name__ == '__main__':
    option = input("Enter 1 to encode or 2 to decode: ")
    if option == '1':
        message = input("Enter the message to encode: ")
        image_path = input(
            "Enter the image name along with extension and full path: ")

        message_inst = Message()
        print("Encoding..")
        message_inst.encode(image_path, message)
        print("Message Encoded successfully")

    elif option == '2':
        image_path = input(
            "Enter the encoded image name along with extension and full path: ")

        message_inst = Message()
        message = message_inst.decode(image_path)
        print("Encoded Message: ", message)

    else:
        print("Exiting..")
        exit()

    # path = input("Enter: ")
    # image = np.array(Image.open(path))
    # # print(image)
    # th = Thresold()
    # thre, curv_mat = th.rgb_sum(image)
    # print("Curvature matrix: ", curv_mat)
    # print("Thresold Value of the Image: ", thre)



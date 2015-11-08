class priorityQueue:

    def __init__(self):
        self.data = []]
    def insert(self, element):
        self.data.append(element)
        self.heapify_up(len(self.data) - 1)

    def peek(self):
        return self.data[0]

    def pop(self):
        temp = self.data[0]
        self.data[0] = self.data[len(self.data) - 1]
        self.data.pop(len(self.data) - 1)
        self.heapify_down(0)
        return temp

    def update_key(self, new, index):
        if(new > self.data[index]):
            self.data[index] = new
            self.heapify_up(index)
        elif(new < self.data[index]):
            self.data[index] = new
            self.heapify_down(index)

    def heapify_down(self, index):
        while(2 * index + 2 == len(self.data) or
                (2 * index + 2 < len(self.data) and 
                (self.data[2 * index + 1] > self.data[index] or 
                self.data[2 * index + 2] > self.data[index]))):
            swap = None
            if(2 * index + 1 == len(self.data) - 1):
                swap = 2 * index + 1
            elif(self.data[2 * index + 1] > self.data[2 * index + 2]):
                swap = 2 * index + 1
            else:
                swap = 2 * index + 2    
            temp = self.data[index]
            self.data[index] = self.data[swap]
            self.data[swap] = temp 
            index = swap

            self.heapify_down(index)

    def heapify_up(self, index):
        print 'heaping up ', index
        while( index > 0 and self.data[(index-1)/2] < self.data[index]):
            swap = (index - 1) / 2

            temp = self.data[index]
            self.data[index] = self.data[swap]
            self.data[swap] = temp
            index = swap
            print "heaped up once: ", self.data
            self.heapify_up(index)


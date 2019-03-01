from random import sample


class HashCode2019Solver:

    class Photo:
        def __init__(self, _id, _orientation, _tags, _size):
            self.id = _id
            self.orientation = _orientation
            self.tags = _tags
            self.size = _size

        def __eq__(self, other):
            return self.id == other.id


    class Slide:
        def __init__(self, _id, _leftPhoto, _rightPhoto = None):
            self.id = _id
            self.leftPhoto = _leftPhoto
            self.rightPhoto = _rightPhoto

            self.tags = _leftPhoto.tags
            self.size = _leftPhoto.size

            if _rightPhoto is not None:
                self.tags += _rightPhoto.tags
                self.size += _rightPhoto.size

        def __eq__(self, other):
            return self.id == other.id


    def __init__(self, input_file, output_file, _subset_size = 1000 ):
        self.input = input_file
        self.output = output_file

        self.Horizontals = list()
        self.Verticals = list()
        self.Slides = dict()
        self.TagsDict = dict()

        self.Slideshow = list()

        self.subset_size = _subset_size

        self._createTagsDict = True

        self.currentSlideId = 0

    def solve(self):
        self.__read()
        self.__joinVerticals()

        ShuffledSlides = sample(list(self.Slides), len(self.Slides))

        if len(self.Slides) < self.subset_size:
            self.Slideshow = self.__solve(ShuffledSlides, self.TagsDict)
        else:
            currentIteration = 1
            iterations = len(ShuffledSlides) // self.subset_size

            currentStart = 0
            Slideshows = {}

            print (f"Gotta Finish {iterations} iterations.")

            while currentStart < len(ShuffledSlides):
                subset = ShuffledSlides[currentStart : currentStart + self.subset_size]
                Slideshows[currentIteration] = self.__solve(subset, self.__createTagsDict(subset))

                currentStart += self.subset_size

                # print (f"Finished iteration {currentIteration}")
                currentIteration += 1

            self.Slideshow = self.__solveSlideshows(Slideshows)

        self.__write()


    def __read(self):
        with open(self.input, 'r') as file:

            photos = file.readline()

            # since we will try to cut slides in chunks and create new dicts for each subset
            # no need to create full dict on input
            if (int(photos) > self.subset_size):
                self._createTagsDict = False

            photo_id = 0

            for line in file:
                tokens = line.split()
                orientation = tokens[0]

                tagsSize = int(tokens[1])

                p = self.Photo(photo_id, orientation, [], tagsSize)

                if orientation == "V":
                    self.Verticals.append(p)

                    for i in range(2, tagsSize + 2):
                        p.tags.append(tokens[i])

                elif orientation == "H":
                    s = self.Slide(self.currentSlideId, p)
                    self.Slides[s.id] = s
                    self.Horizontals.append(p)
                    self.currentSlideId += 1

                    for i in range(2, tagsSize + 2):

                        if self._createTagsDict:
                            if tokens[i] in self.TagsDict:
                                self.TagsDict[tokens[i]].append(s.id)
                            else:
                                self.TagsDict[tokens[i]] = [s.id]

                        p.tags.append(tokens[i])

                photo_id += 1

    def __joinVerticals(self):
        self.Verticals = sorted(self.Verticals, key=lambda photo: photo.size)

        n = len(self.Verticals)

        if n % 2 == 0:
            start = 0
        else:
            start = 1

        for i in range(start, n // 2):

            s = self.Slide(self.currentSlideId, self.Verticals[i], self.Verticals[n - 1 - i])
            self.currentSlideId += 1

            self.Slides[s.id] = s

            if self._createTagsDict:
                for tag in s.tags:
                    if tag not in self.TagsDict:
                        self.TagsDict[tag] = [s.id]
                    else:
                        self.TagsDict[tag].append(s.id)

    def __write(self):
        with open(self.output, "w+") as file:
            file.write(str(len(self.Slideshow)) + '\n')

            for slide in self.Slideshow:
                file.write(str(slide.leftPhoto.id))

                if slide.rightPhoto is not None:
                    file.write(' ' + str(slide.rightPhoto.id))

                file.write('\n')


    def __createTagsDict(self, slides):
        TagsDict = {}

        for slide_id in slides:
            for tag in self.Slides[slide_id].tags:
                if tag in TagsDict:
                    TagsDict[tag].append(slide_id)
                else:
                    TagsDict[tag] = [slide_id]

        return TagsDict

    def __solve(self, slides, TagsDict):
        # set of keys
        SlideSet = set(slides)
        Visited = set()
        Slideshow = []

        current_id = max (SlideSet, key=lambda slide: self.Slides[slide].size)
        # current_id = next(iter(SlideSet))
        Slideshow.append(self.Slides[current_id])

        while len(SlideSet) != 0:
            commons = dict()

            SlideSet.remove(current_id)
            Visited.add(current_id)

            for tag in self.Slides[current_id].tags:

                for slide_id in TagsDict[tag]:

                    if slide_id in Visited:
                        continue

                    if slide_id in commons:
                        commons[slide_id] += 1
                    else:
                        commons[slide_id] = 1

            if len(commons) == 0:
                if len(SlideSet) == 0:
                    break

                current_id = next(iter(SlideSet))
            else:
                scores = []
                for slide_id, num_comm in commons.items():
                    # scores = [score, slide_id]
                    scores.append((min( [ self.Slides[current_id].size - num_comm, num_comm, self.Slides[slide_id].size - num_comm ] ), slide_id) ) # (score, slide)

                _score, slide_id = max(scores, key=lambda score: scores[0])

                current_id = slide_id

            Slideshow.append(self.Slides[current_id])

        return Slideshow


    def __createSlideshowTagsDict(self, Slideshows):
        TagsDict = {}
        
        for key, show in Slideshows.items():
            for tag in show[0].tags:
                if tag in TagsDict:
                    TagsDict[tag].append(key)
                else:
                    TagsDict[tag] = [key]

        return TagsDict

    def __solveSlideshows(self, Slideshows):
        fullShow = []

        TagsDict = self.__createSlideshowTagsDict(Slideshows)

        # set of keys
        SlideshowsSet = set(list(Slideshows))
        Visited = set()

        current_show_id = max (SlideshowsSet, key=lambda show: Slideshows[show][-1].size)
        # current_show_id = next(iter(SlideshowsSet))
        fullShow += Slideshows[current_show_id]

        while len(SlideshowsSet) != 0:
            commons = dict()

            SlideshowsSet.remove(current_show_id)
            Visited.add(current_show_id)

            # We are searching for the next slideshow to stick to current slideshow
            # That means we must stick the right-most slide of current to the left-most slide of next
            for tag in Slideshows[current_show_id][-1].tags:

                if tag not in TagsDict:
                    continue

                for show_id in TagsDict[tag]:

                    if show_id == current_show_id:
                        continue

                    if show_id in Visited:
                        continue

                    if show_id in commons:
                        commons[show_id] += 1
                    else:
                        commons[show_id] = 1

            if len(commons) == 0:
                if len(SlideshowsSet) == 0:
                    break

                current_show_id = next(iter(SlideshowsSet))
            else:
                scores = []
                for show_id, num_comm in commons.items():
                    # scores = [score, slide_id]
                    scores.append( (min( [ Slideshows[current_show_id][-1].size - num_comm, \
                    num_comm, \
                    Slideshows[show_id][-1].size - num_comm ] ), show_id) ) # (score, show)

                _score, show_id = max(scores, key=lambda score: scores[0])

                current_show_id = show_id

            fullShow += Slideshows[current_show_id]

        return fullShow
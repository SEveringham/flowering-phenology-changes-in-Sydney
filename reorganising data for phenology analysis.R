### playing around with sydney flowering time data

#load required libraries
library(dplyr)
library(tidyr)
library(measurements)
library(maptools)
library(maps)
library(ggmap)
library(lubridate)
library(scales)
library(ggplot2)
library(broom)
library(rgdal)
library(satellite)

#read in data
nswherb <- read.csv("herbtargetlist.csv", stringsAsFactors = F)
sydneyuniherb <- read.csv("sydneyuniherbarium.csv", stringsAsFactors = F)
macquarieherb <- read.csv("macquarieuniherb.csv", stringsAsFactors = F)
unswherb <- read.csv("unswherb.csv", stringsAsFactors = F)
fielddata <- read.csv("myfielddata.csv", stringsAsFactors = F)
pricedata <- read.csv("Price1960data.csv", stringsAsFactors = F)

#join all the data together
mydata <- rbind(nswherb, sydneyuniherb, macquarieherb, unswherb, fielddata, pricedata)

#a few variables need to be converted to numeric
mydata$Latdeg <- as.numeric(mydata$Latdeg)
mydata$Latmin <- as.numeric(mydata$Latmin)
mydata$Latsec <- as.numeric(mydata$Latsec)
mydata$Longdeg <- as.numeric(mydata$Longdeg)
mydata$Longsec <- as.numeric(mydata$Longsec)
mydata$Longmin <- as.numeric(mydata$Longmin)
mydata$Species <- as.factor(mydata$Species)

mydata$Latsec[is.na(mydata$Latsec)] <- 0 #calling the NAs in the seconds column zeros because the calculation of decimal degrees can't handle NAs but can handle zeros
mydata$Longsec[is.na(mydata$Longsec)] <- 0 #same as ^

mydata <- mydata %>% mutate(Lat = - (Latdeg + Latmin / 60 + Latsec / 60^2),
          Long = Longdeg + Longmin / 60 + Longsec / 60^2) #### converting degrees minutes seconds to decimal degrees

#convert data to date format correctly

mydata <- mydata %>% mutate(datelong= as.Date(mydata$Date, "%d/%m/%Y"))

#want to filter data to remove species that lay outside of the northern sydney region
mydata <- mydata %>% filter(Lat >= -33.84, Long >=151.03)

#save data as a csv for further analyses 

write.csv(mydata, "floweringdatafull.csv")



##making a map :D

#create a buffer to make edges of the map just past my site locations
buffer <- 0.1

#make map bounds
geo_bounds <- c(left = min(mydata$Long)-buffer,
                bottom = min(mydata$Lat)-buffer,
                right = max(mydata$Long)+buffer,
                top = max(mydata$Lat)+buffer)

Sites.grid <- expand.grid(lon_bound = c(geo_bounds[1], geo_bounds[3]), 
                          lat_bound = c(geo_bounds[2], geo_bounds[4]))

coordinates(Sites.grid) <- ~ lon_bound + lat_bound

Aus <- readOGR(dsn = "61395_shp/australia",layer = "cstauscd_r")
Aus_coast <- subset(Aus, FEAT_CODE != "sea")

## cropping Australia to fit our data points
Aus_crop <- crop(Aus_coast, extent(Sites.grid))
plot(Aus_crop)

# plotting my map
Sydneymap <- ggplot() + 
  geom_polygon(data = Aus_crop, aes(x=long, y=lat, group=group), fill = "white", colour="black") +
  coord_equal() +
  geom_point(data=mydata, aes(x=Long, y=Lat), color="darkolivegreen4", size=4, alpha = 0.3) +
  labs(x="Longitude", y="Latitude") +
  theme_classic() +
  theme(axis.text.x = element_text(size=40),
        axis.text.y = element_text(size=40),
        axis.title.x = element_text(size=40),
        axis.title.y = element_text(size=40)) +
  theme(legend.title = element_text(size=45),
        legend.text = element_text(size=40))

plot(Sydneymap)


tiff("mymap.tiff", height=1000, width=1000)
plot(Sydneymap)
dev.off()
##this visualisation has now helped me to find outliers in the data and maybe points where the lat/longs were written incorrectly

### Running some analyses

#get a plot of specimen sampled each year

specimenplot <- ggplot(data = subset(mydata,  DataType == "Herbarium"), aes(x=datelong)) + geom_histogram(fill = "darkseagreen4", colour="black", size=0.1, bins = 60) +
  scale_x_date(labels = date_format("%Y"),
               breaks = "20 year") +
  xlab("") +
  ylab("Number of Records") +
  theme_classic(base_size=25)
plot(specimenplot)

tiff("number of specs.tiff", res = 300, width = 4000, height=2000)
plot(specimenplot)
dev.off()
import java.util.*;

class Car {
    int index;
    int arrival;
    int street;

    Car(int index, int arrival, int street) {
        this.index = index;
        this.arrival = arrival;
        this.street = street;
    }
}

public class Main {
    public static void main(String[] args) {
        int[] arrival = { 0, 0, 1, 4 };
        int[] street = { 0, 1, 1, 0 };
        int[] result = getResults(arrival, street);
        for (int i = 0; i < result.length; i++) {
            System.out.println(result[i]);
        }
    }

    public static int[] getResults(int[] arrival, int[] street) {
        Queue<Car> ave = new LinkedList<>();
        Queue<Car> strt = new LinkedList<>();

        int[] result = new int[arrival.length];

        for (int i = 0; i < arrival.length; i++) {
            Car car = new Car(i, arrival[i], street[i]);
            if (street[i] == 0)
                strt.add(car);
            else if (street[i] == 1)
                ave.add(car);
        }

        int counter = 0;
        int previous = -1;

        while (!ave.isEmpty() || !strt.isEmpty()) {
            Car nextCar;
            if (ave.isEmpty()) {
                nextCar = strt.peek();
                if (counter < nextCar.arrival) {
                    previous = -1;
                    counter++;
                    continue;
                }
            } else if (strt.isEmpty()) {
                nextCar = ave.peek();
                if (counter < nextCar.arrival) {
                    previous = -1;
                    counter++;
                    continue;
                }
            } else {
                Car streetCar = strt.peek();
                Car aveCar = ave.peek();

                if (counter >= aveCar.arrival && counter >= streetCar.arrival) {
                    if (previous == -1 || previous == 1) {
                        nextCar = aveCar;
                        previous = 1;
                    } else {
                        nextCar = streetCar;
                        previous = 0;
                    }
                } else if (counter >= aveCar.arrival) {
                    nextCar = aveCar;
                    previous = 1;
                } else if (counter >= streetCar.arrival) {
                    nextCar = streetCar;
                    previous = 0;
                } else {
                    previous = -1;
                    counter++;
                    continue;
                }
            }

            result[nextCar.index] = counter;
            counter++;
            if (nextCar.street == 0)
                strt.remove();
            else if (nextCar.street == 1)
                ave.remove();
        }
        return result;
    }

}

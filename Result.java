import java.util.*;;

class UnionFind {
    int[] parent;
    HashSet<Integer> members;

    public UnionFind(HashSet<Integer> set) {
        members = set;
        parent = new int[101];
        for (int s : set) {
            parent[s] = s;
        }
    }

    public int Find(int s) {
        if (s == parent[s]) {
            return s;
        }
        return parent[s] = Find(parent[s]);
    }

    public void Union(int s1, int s2) {
        int parent_s1 = Find(s1);
        int parent_s2 = Find(s2);

        if (parent_s1 != parent_s2) {
            parent[parent_s1] = parent_s2;
        }
    }

    public int getMax() {
        int[] roots = new int[101];
        for (int i = 1; i < 101; i++) {
            if (parent[i] != 0) {
                roots[i] = Find(i);
            }
        }

        HashMap<Integer, ArrayList<Integer>> rootCount = new HashMap<>();
        for (int i = 0; i < roots.length; i++) {
            if (roots[i] == 0)
                continue;
            int root = roots[i];
            ArrayList<Integer> list = new ArrayList<>();
            if (rootCount.containsKey(root))
                list = rootCount.get(root);
            list.add(i);
            rootCount.put(root, list);
        }

        ArrayList<ArrayList<Integer>> maxGroups = new ArrayList<>();
        int max = 0;
        for (ArrayList<Integer> list : rootCount.values()) {
            if (list.size() > max) {
                max = list.size();
                maxGroups = new ArrayList<>();
                maxGroups.add(list);
            } else if (list.size() == max) {
                maxGroups.add(list);
            }
        }

        int maxProduct = 0;
        for (ArrayList<Integer> list : maxGroups) {
            Collections.sort(list, Collections.reverseOrder());
            maxProduct = Math.max(maxProduct, list.get(0) * list.get(1));
        }
        return maxProduct;
    }
}

class Result {

    public static void main(String[] args) {
        List<Integer> friends_from = new ArrayList<>();
        List<Integer> friends_to = new ArrayList<>();
        List<Integer> friends_weight = new ArrayList<>();

        int[] friends_from_arr = { 1, 1, 1, 1, 2, 2, 3, 3, 3, 3, 3, 4, 4, 5, 5, 5, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 8, 8,
                8, 8, 8, 8, 9, 9, 9, 10, 10, 10, 10, 11, 11, 11, 11, 12, 12, 12, 12, 12, 12, 13, 13, 13, 14, 14, 14, 14,
                14, 14, 14, 14, 14, 15, 15, 15, 16, 16, 17, 17, 17, 17, 17, 18, 19, 19, 19, 19, 19, 19, 19, 20, 20, 20,
                20, 20, 20, 21, 21, 21, 22, 22, 22, 22, 22, 22, 23, 23, 23, 23, 24, 24, 24, 25, 25, 25, 25, 25, 25, 25,
                26, 26, 26, 26, 26, 27, 27, 27, 28, 28, 28, 29, 29, 29, 30, 30, 30, 30, 31, 31, 31, 31, 31, 32, 32, 32,
                32, 33, 33, 33, 34, 35, 35, 35, 35, 35, 35, 35, 36, 36, 36, 36, 36, 37, 37, 37, 37, 37, 37, 38, 38, 39,
                39, 40, 40, 41, 41, 41, 41, 41, 42, 43, 44, 44, 44, 45, 45, 45, 45, 46, 46, 46, 46, 47, 47, 48, 48, 48,
                48, 48, 48, 49, 49, 49, 49, 49, 50, 50, 50, 50, 50, 50 };
        for (int x : friends_from_arr)
            friends_from.add(x);

        int[] friends_to_arr = { 2, 4, 19, 41, 1, 16, 1, 7, 15, 16, 18, 6, 8, 15, 31, 31, 2, 9, 30, 33, 34, 42, 17, 39,
                47, 48, 1, 2, 28, 28, 36, 38, 12, 24, 29, 11, 14, 16, 42, 2, 44, 45, 46, 5, 13, 15, 25, 28, 50, 8, 31,
                32, 1, 4, 7, 11, 13, 22, 28, 34, 44, 21, 47, 49, 20, 29, 5, 37, 40, 44, 50, 28, 21, 24, 24, 26, 27, 29,
                39, 23, 30, 42, 46, 47, 50, 15, 34, 38, 14, 21, 23, 23, 38, 48, 26, 28, 36, 41, 14, 37, 49, 6, 8, 11,
                44, 45, 47, 50, 16, 18, 18, 19, 22, 5, 19, 32, 2, 25, 26, 4, 14, 42, 6, 36, 37, 50, 3, 5, 36, 47, 47, 7,
                22, 40, 46, 20, 34, 46, 47, 5, 7, 18, 21, 22, 27, 47, 6, 17, 39, 41, 50, 2, 10, 21, 32, 33, 40, 4, 18,
                13, 30, 15, 25, 7, 15, 16, 24, 28, 23, 34, 9, 18, 49, 1, 6, 25, 29, 1, 12, 22, 49, 10, 25, 11, 13, 20,
                28, 34, 36, 8, 24, 32, 34, 39, 6, 17, 23, 24, 47, 48 };
        for (int x : friends_to_arr)
            friends_to.add(x);

        int[] friends_weight_arr = { 26, 74, 22, 54, 48, 53, 42, 65, 13, 32, 73, 10, 39, 78, 54, 97, 89, 24, 24, 61, 14,
                89, 47, 98, 69, 23, 14, 82, 29, 73, 91, 78, 44, 95, 87, 90, 20, 11, 17, 7, 15, 63, 64, 87, 23, 18, 60,
                24, 7, 64, 28, 75, 45, 3, 92, 89, 98, 81, 40, 41, 69, 22, 73, 95, 13, 66, 64, 92, 74, 11, 48, 81, 64,
                22, 58, 13, 58, 28, 95, 78, 100, 4, 14, 20, 38, 89, 45, 46, 89, 3, 13, 36, 92, 7, 5, 44, 95, 47, 81, 32,
                46, 60, 40, 39, 51, 78, 1, 24, 39, 30, 95, 11, 52, 27, 45, 55, 13, 95, 34, 35, 67, 5, 5, 19, 48, 27, 70,
                82, 96, 24, 53, 26, 76, 15, 56, 82, 21, 2, 2, 15, 78, 87, 20, 76, 72, 11, 16, 22, 12, 98, 86, 56, 53,
                48, 16, 18, 65, 37, 59, 17, 80, 4, 12, 52, 11, 67, 7, 43, 49, 49, 10, 50, 42, 50, 74, 67, 5, 89, 94, 73,
                98, 63, 58, 15, 40, 9, 43, 88, 53, 50, 91, 91, 98, 90, 97, 35, 34, 8, 87, 95 };
        for (int x : friends_weight_arr)
            friends_weight.add(x);

        countCompanies(friends_from, friends_to, friends_weight);
    }

    /*
     * Complete the 'countCompanies' function below.
     *
     * The function is expected to return an INTEGER.
     * The function accepts following parameters:
     * 1. INTEGER friends_nodes
     * 2. INTEGER_ARRAY friends_from
     * 3. INTEGER_ARRAY friends_to
     * 4. INTEGER_ARRAY friends_weight
     */

    public static int countCompanies(List<Integer> friends_from, List<Integer> friends_to,
            List<Integer> friends_weight) {
        HashMap<Integer, HashSet<Integer>> setMap = new HashMap<>();
        for (int i = 0; i < friends_from.size(); i++) {
            int company = friends_weight.get(i);
            HashSet<Integer> companySet = new HashSet<>();

            if (setMap.containsKey(company))
                companySet = setMap.get(company);

            companySet.add(friends_from.get(i));
            companySet.add(friends_to.get(i));
            setMap.put(company, companySet);
        }

        int result = 0;
        for (int company : setMap.keySet()) {
            UnionFind unionFind = new UnionFind(setMap.get(company));

            for (int i = 0; i < friends_from.size(); i++) {
                if (friends_weight.get(i) == company)
                    unionFind.Union(friends_from.get(i), friends_to.get(i));
            }
            result = Math.max(result, unionFind.getMax());
        }
        return result;
    }
}
#include <bits/stdc++.h>
using namespace std;
using ll = long long;
using pii = pair<int,int>;
using pll = pair<ll,ll>;
const int inf = 1073741823;
const ll infl = 1LL << 60;

// T: 要素の型, SizeT: 要素数の型（デフォルトは int）
template <typename T, typename SizeT = ll>
vector<T> read_vec(SizeT n)
{
    vector<T> v(n);
    for (auto &x : v)
        cin >> x;
    return v;
}

// 2次元版
template <typename T, typename SizeT = ll>
vector<vector<T>> read_vec2(SizeT h, SizeT w)
{
    vector<vector<T>> v(h, vector<T>(w));
    for (auto &row : v)
    {
        for (auto &x : row)
            cin >> x;
    }
    return v;
}


// 出力モードの定義
enum PrintMode {
    SPACE,  // 空白区切り
    LINE,   // 改行区切り
    CONCAT  // 区切りなし（連結）
};

// vectorをPrintemodeに従って出力
template<typename T> 
inline void print_vec(const vector<T> &v, PrintMode mode = SPACE) {
    if(v.empty()){
        cout << "This vector is empty." << endl;
        return;
    }

    for (int i = 0; i < (int)v.size(); i++) {
        // 値の出力
        cout << v[i];

        // 区切り文字の制御
        if (i + 1 == (int)v.size()) {
            cout << endl; // 最後の要素は必ず改行
        } else {
            if (mode == SPACE) cout << ' ';
            else if (mode == LINE) cout << endl;
            // CONCAT の場合は何も出力しない
        }
    }
}

// YesNO出力
template <typename T, typename YT = const char*, typename NT = const char*>
void yn(T hantei, YT yes = "Yes", NT no = "No")
{
    if (hantei)
    {
        cout << yes << endl;
    }
    else
    {
        cout << no << endl;
    }
}

// 2つの型のうち、より広い範囲を扱える型（共通型）を判定する
template <typename T, typename U>
using common_int_t = typename common_type<T, U>::type;

// floor_div: a / b (負の無限大方向への切り捨て)
template <typename T, typename U>
auto floor_div(T a, U b) {
    if (b == 0) throw runtime_error("Division by zero");
    
    using C = common_int_t<T, U>;
    C ca = a;
    C cb = b;
    
    C res = ca / cb;
    C rem = ca % cb;
    
    // 異符号かつ余りがある場合、-1する
    if ((ca ^ cb) < 0 && rem != 0) {
        res--;
    }
    return res;
}

// floor_mod: a % b (除数 b の符号に合わせる)
template <typename T, typename U>
auto floor_mod(T a, U b) {
    if (b == 0) throw runtime_error("Division by zero");
    
    using C = common_int_t<T, U>;
    C ca = a;
    C cb = b;
    
    C res = ca % cb;
    
    // 異符号かつ余りがある場合、b を足す
    if ((ca ^ cb) < 0 && res != 0) {
        res += cb;
    }
    return res;
}

// 2つの引数を比較して、1つ目の値が2つ目の値より大きい(or小さい)なら更新しつつtrueを返す
template<typename T1, typename T2> inline bool chmax(T1 &a, T2 b) {
    bool compare = a < b;
    if(compare) a = b;
    return compare;
}
template<typename T1, typename T2> inline bool chmin(T1 &a, T2 b) {
    bool compare = a > b;
    if(compare) a = b;
    return compare;
}

// 1つ目の値 a が 2つ目の値 b より小さいなら a=b とし、
// さらに 3つ目の変数 target を 4つ目のソース source で更新して true を返す
template<typename T1, typename T2, typename T3, typename T4>
inline bool chmax(T1 &a, T2 b, T3 &target, const T4 &source) {
    bool compare = a < b;
    if (compare) {
        a = b;
        target = source; // 最大値が更新されたら、付随するデータも更新
    }
    return compare;
}

template<typename T1, typename T2, typename T3, typename T4>
inline bool chmin(T1 &a, T2 b, T3 &target, const T4 &source) {
    bool compare = a > b;
    if (compare) {
        a = b;
        target = source;
    }
    return compare;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    ll n, m;
    cin >> n >> m;

    // マルチテストケース
    long long t;
    cin >> t;
    while (t--)
    {
        ;
    }

    // longlong型の1次元配列宣言と入力
    auto A = read_vec<ll>(n);

    // 1次元配列のループ(参照渡し　値コピーするには&を外す)
    for (auto &AA : A)
    {
        cout << AA << endl;
    }

    // longlong型の2次元配列宣言と入力
    auto A2 = read_vec2<ll>(n, m);

    return 0;
}
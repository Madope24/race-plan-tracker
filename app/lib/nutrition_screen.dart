import 'package:flutter/material.dart';

import 'state.dart';
import 'ui.dart';
import 'util.dart';

String tzs(num? v) {
  if (v == null) return '-';
  final s = v.round().toString();
  final b = StringBuffer();
  for (var i = 0; i < s.length; i++) {
    if (i > 0 && (s.length - i) % 3 == 0) b.write(',');
    b.write(s[i]);
  }
  return '$b TZS';
}

/// Nutrition: today's targets and meals (Tanzanian foods, grams, macros, cost), supplements, smoothies, shopping list.
class NutritionScreen extends StatelessWidget {
  final AppState st;
  const NutritionScreen({super.key, required this.st});

  @override
  Widget build(BuildContext context) {
    final iso = st.currentIso;
    final pd = st.planDay(iso);
    final l = st.log(iso);
    final n = asMap(st.plan['nutrition']);
    final meals = st.mealsFor(iso);
    final eaten = asList(l['meals_eaten']).map(asStr).toSet();
    final mp = asStr(pd['meal_plan']);
    double v(String k) => asNum(l[k]) ?? 0.0;
    double t(String k) => asNum(pd[k]) ?? 1;
    void go(String title, List<Widget> Function() body) => pushPage(context, title, st, body);
    final planName = {'CUT': 'Cutting plan', 'FUEL': 'Fuelling plan', 'FAST': 'Fasting-day plan', 'RAMADAN': 'Ramadan plan'}[mp] ?? mp;
    return ListView(padding: const EdgeInsets.only(bottom: 28), children: [
      Section(
        title: 'Today\'s targets',
        subtitle: '$planName · ${pd['fasting'] == true ? 'dry fast until ${asStr(asMap(st.effective('fasting'))['break_time'])}' : 'no breakfast'}',
        children: [
          Row(mainAxisAlignment: MainAxisAlignment.spaceAround, children: [
            Ring(value: v('kcal') / t('kcal'), label: '${v('kcal').round()}', sub: 'of ${t('kcal').round()} kcal', color: C.accent, size: 84),
            Ring(value: v('protein') / t('protein'), label: '${v('protein').round()}g', sub: 'of ${t('protein').round()} protein', color: C.teal, size: 84),
            Ring(value: v('water') / t('water_l'), label: '${fmtNum(v('water'))}L', sub: 'of ${fmtNum(t('water_l'))} L water', color: C.swim, size: 84),
          ]),
          const SizedBox(height: 12),
          KV('Carbohydrates', '${v('carbs').round()} of ${t('carbs').round()} g'),
          KV('Fat', '${v('fat').round()} of ${t('fat').round()} g (at least 65 g for hormonal health)'),
          const SizedBox(height: 8),
          Row(children: [
            OutlinedButton(onPressed: () => st.addWater(iso, 0.25), child: const Text('+250 ml water')),
            const SizedBox(width: 8),
            OutlinedButton(onPressed: () => go('Log food by hand', () => [_manual(iso)]), child: const Text('Enter by hand')),
          ]),
        ],
      ),
      Padding(
        padding: const EdgeInsets.fromLTRB(18, 10, 18, 2),
        child: Text('MEALS TODAY: tick what you ate', style: TextStyle(color: C.mut, fontSize: 12, fontWeight: FontWeight.w800, letterSpacing: 1)),
      ),
      for (final m in meals) _meal(context, iso, m, eaten.contains(asStr(m['meal']))),
      if (pd['smoothie'] != null)
        Section(title: 'Smoothie day: ${asStr(pd['smoothie'])}', subtitle: 'Optional, 16:00. Counts as a snack, not a free drink.', children: const []),
      _supplements(context, iso, l),
      Section(title: 'More', children: [
        _link(Icons.local_drink, 'Smoothies', () => go('Smoothies', () => _smoothies(n))),
        _link(Icons.shopping_basket, 'Weekly shopping list', () => go('Shopping list', () => _shopping(n))),
        _link(Icons.directions_run, 'Sports nutrition and race fuelling', () => go('Sports nutrition', () => _sports(n))),
        _link(Icons.calendar_view_week, 'All meal plans', () => go('Meal plans', () => _mealPlans(n))),
        _link(Icons.eco, 'Healthy eating and swaps', () => go('Healthy eating', () => _eating(n))),
        _link(Icons.favorite, 'Hormonal health', () => go('Hormonal health', () => _hormone(n))),
        _link(Icons.list_alt, 'Tanzanian food database', () => go('Foods', () => _foods(n))),
      ]),
    ]);
  }

  Widget _link(IconData i, String t, VoidCallback f) => ListTile(
      contentPadding: EdgeInsets.zero,
      leading: Icon(i, color: C.accent),
      title: Text(t, style: TextStyle(color: C.text)),
      trailing: Icon(Icons.chevron_right, color: C.mut),
      onTap: f);

  Widget _manual(String iso) {
    final l = st.log(iso);
    Widget nb(String k, String label, String sfx) =>
        NumField(key: ValueKey('man-$iso-$k'), label: label, suffix: sfx, value: asNum(l[k]), onChanged: (v) => st.setField(iso, k, v));
    return Section(title: 'Food eaten today', subtitle: 'Overrides the totals from ticked meals.', children: [
      Row(children: [Expanded(child: nb('kcal', 'Calories', 'kcal')), const SizedBox(width: 10), Expanded(child: nb('protein', 'Protein', 'g'))]),
      const SizedBox(height: 10),
      Row(children: [Expanded(child: nb('carbs', 'Carbohydrates', 'g')), const SizedBox(width: 10), Expanded(child: nb('fat', 'Fat', 'g'))]),
      const SizedBox(height: 10),
      nb('water', 'Water', 'L'),
    ]);
  }

  Widget _meal(BuildContext context, String iso, Map<String, dynamic> m, bool done) {
    final t = asMap(m['totals']);
    return Section(
      title: '${asStr(m['time'])}  ${asStr(m['meal'])}',
      subtitle: '${asStr(t['kcal'])} kcal · ${fmtNum(asNum(t['p']))} g protein · ${fmtNum(asNum(t['c']))} g carbs · ${fmtNum(asNum(t['f']))} g fat · about ${tzs(asNum(m['tzs']))}',
      accent: done ? C.ok : null,
      trailing: Checkbox(value: done, onChanged: (_) => st.toggleMeal(iso, asStr(m['meal']))),
      children: [
        for (final i in asList(m['items']).map(asMap))
          Text('• ${asStr(i['grams'])} g ${asStr(i['food'])}  (${asStr(i['kcal'])} kcal, ${fmtNum(asNum(i['p']))} g protein)',
              style: TextStyle(fontSize: 13.5, height: 1.4, color: C.text)),
        if (asStr(m['how']).isNotEmpty)
          Theme(
            data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
            child: ExpansionTile(
              tilePadding: EdgeInsets.zero,
              title: Text('How to prepare', style: TextStyle(color: C.accent, fontWeight: FontWeight.w600, fontSize: 13.5)),
              children: [Text(asStr(m['how']), style: TextStyle(color: C.text, height: 1.4, fontSize: 13.5))],
            ),
          ),
      ],
    );
  }

  Widget _supplements(BuildContext context, String iso, Map<String, dynamic> l) {
    final sups = asList(st.plan['supplements']).map(asMap).toList();
    final taken = asList(l['supps_taken']).map(asStr).toSet();
    final mine = sups.where((s) => s['in_plan'] == true).toList();
    return Section(
      title: 'Supplements today',
      subtitle: 'Tick what you actually took. Tap a name for evidence, doses and cautions.',
      children: [
        for (final s in mine)
          Row(children: [
            Checkbox(value: taken.contains(asStr(s['name'])), onChanged: (_) => st.toggleInList(iso, 'supps_taken', asStr(s['name']))),
            Expanded(
              child: InkWell(
                onTap: () => pushPage(context, 'Supplements', st, () => _suppInfo(sups)),
                child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Text(asStr(s['name']), style: TextStyle(color: C.text, fontWeight: FontWeight.w600)),
                  Text(asStr(s['when']), style: TextStyle(color: C.mut, fontSize: 12)),
                ]),
              ),
            ),
          ]),
        TextButton(onPressed: () => pushPage(context, 'Supplements', st, () => _suppInfo(sups)), child: const Text('All supplements and evidence')),
      ],
    );
  }

  List<Widget> _suppInfo(List<Map<String, dynamic>> sups) => [
        for (final s in sups)
          Section(
            title: asStr(s['name']),
            subtitle: s['in_plan'] == true ? 'In your plan' : 'Not in your plan',
            trailing: Pill(asStr(s['evidence']).split(' ').first, color: s['in_plan'] == true ? C.teal : C.mut),
            children: [
              Para('Purpose', asStr(s['purpose'])),
              Para('Evidence', asStr(s['evidence'])),
              Para('Studied dose range', asStr(s['dose'])),
              Para('Timing', asStr(s['when'])),
              Para('Possible side effects', asStr(s['side_effects'])),
              Para('Cautions and medical notes', asStr(s['cautions'])),
            ],
          ),
        Padding(padding: const EdgeInsets.all(16), child: Text(asStr(st.plan['supplements_note']), style: TextStyle(color: C.mut, height: 1.4))),
      ];

  List<Widget> _mealPlans(Map<String, dynamic> n) {
    final plans = asMap(n['meal_plans']);
    final out = <Widget>[];
    const names = {'CUT': 'Cutting plan: until the weight goal date', 'FUEL': 'Fuelling plan: after it', 'FAST': 'Fasting days (dry fast)', 'RAMADAN': 'Ramadan'};
    for (final name in names.keys) {
      final p = asMap(plans[name]);
      out.add(Padding(
        padding: const EdgeInsets.fromLTRB(18, 14, 18, 4),
        child: Text(names[name]!, style: TextStyle(fontSize: 17, fontWeight: FontWeight.w800, color: C.text)),
      ));
      final daysShown = (name == 'FAST' || name == 'RAMADAN') ? ['Mon'] : kWeekdays;
      for (final day in daysShown) {
        final d = asMap(p[day]);
        final tot = asMap(d['totals']);
        out.add(Section(
          title: (name == 'FAST' || name == 'RAMADAN') ? 'Each day' : day,
          subtitle: '${asStr(tot['kcal'])} kcal · ${asStr(tot['p'])} g protein · ${asStr(tot['c'])} g carbs · ${asStr(tot['f'])} g fat · about ${tzs(asNum(tot['tzs']))}',
          children: [
            for (final m in asList(d['meals']).map(asMap))
              Para('${asStr(m['time'])}  ${asStr(m['meal'])}', asList(m['items']).map(asMap).map((i) => '${asStr(i['grams'])} g ${asStr(i['food'])}').join(', ')),
          ],
        ));
      }
    }
    return out;
  }

  List<Widget> _smoothies(Map<String, dynamic> n) => [
        Padding(padding: const EdgeInsets.all(16), child: Text(asStr(n['smoothie_rule']), style: TextStyle(color: C.mut, height: 1.4))),
        for (final s in asList(n['smoothies']).map(asMap))
          Section(
            title: asStr(s['name']),
            subtitle: '${asStr(asMap(s['totals'])['kcal'])} kcal · ${asStr(asMap(s['totals'])['p'])} g protein · ${asStr(asMap(s['totals'])['c'])} g carbs · about ${tzs(asNum(s['tzs']))}',
            children: [
              Para('When it helps', asStr(s['when'])),
              Para('Why', asStr(s['why'])),
              Para('Ingredients', asList(s['items']).map(asMap).map((i) => '${asStr(i['grams'])} g ${asStr(i['food'])}').join('\n')),
              Para('How', asStr(s['how'])),
            ],
          ),
      ];

  List<Widget> _shopping(Map<String, dynamic> n) {
    final sh = asMap(n['shopping']);
    const names = {'CUT': 'Cutting weeks', 'FUEL': 'Fuelling weeks', 'RAMADAN': 'Ramadan weeks'};
    return [
      Padding(
        padding: const EdgeInsets.all(16),
        child: Text('Built from the meal plans (fasting days included). Prices are approximate Dar es Salaam market prices; amounts are as eaten (cooked weight for rice, ugali and beans).',
            style: TextStyle(color: C.mut, height: 1.4)),
      ),
      for (final k in names.keys)
        Section(title: names[k]!, subtitle: 'About ${tzs(asNum(asMap(sh[k])['total']))} a week', children: [
          for (final r in asList(asMap(sh[k])['rows']).map(asMap)) KV(asStr(r['where']), '${asStr(r['item'])}: ${asStr(r['amount'])} · ${tzs(asNum(r['tzs']))}'),
        ]),
    ];
  }

  List<Widget> _sports(Map<String, dynamic> n) => [
        Section(title: 'Sports nutrition', children: [for (final s in asList(n['sports']).map(asMap)) Para(asStr(s['topic']), asStr(s['detail']))]),
        Section(title: 'Race-fuelling practice before the 70.3', subtitle: 'Carbohydrate per hour on long sessions: train your gut gradually', children: [
          for (final s in asList(n['fuel_progression']).map(asMap)) KV(asStr(s['when']), asStr(s['carbs'])),
        ]),
      ];

  List<Widget> _eating(Map<String, dynamic> n) => [
        Section(title: 'Rules', children: [for (final r in asList(n['rules']).map(asMap)) Para(asStr(r['rule']), asStr(r['detail']))]),
        Section(title: 'Easy swaps', children: [
          for (final r in asList(n['swaps']).map(asMap)) Para('Instead of ${asStr(r['instead'])}', 'Have ${asStr(r['have'])}', extra: 'Saves ${asStr(r['saves'])}')
        ]),
      ];

  List<Widget> _hormone(Map<String, dynamic> n) => [
        Section(title: 'Supporting normal hormonal health', children: [for (final r in asList(n['hormone']).map(asMap)) Para(asStr(r['topic']), asStr(r['detail']))]),
      ];

  List<Widget> _foods(Map<String, dynamic> n) => [
        Section(title: 'Per 100 g', subtitle: 'Rounded values from standard food tables; local recipes vary. Prices approximate.', children: [
          for (final f in asList(n['foods']).map(asMap))
            Para(asStr(f['name']), '${asStr(f['kcal'])} kcal · ${asStr(f['p'])} g protein · ${asStr(f['c'])} g carbs · ${asStr(f['f'])} g fat',
                extra: '${asStr(f['english'])} · ${asStr(f['group'])} · ${asStr(f['portion'])} · about ${tzs(asNum(f['tzs_kg']))} per kg'),
        ]),
      ];
}

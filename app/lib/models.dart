// Data models matching the Race Plan API.

double? _d(dynamic v) => v == null ? null : (v as num).toDouble();
int? _i(dynamic v) => v == null ? null : (v as num).toInt();
bool? _b(dynamic v) => v == null ? null : v as bool;

String nowUtcIso() => DateTime.now().toUtc().toIso8601String();

class SessionLog {
  final String status; // done | partial | skipped
  final double? actual;
  final int? effort;
  final double? durationMin;
  final String? notes;
  final String updatedAt;

  SessionLog({
    required this.status,
    this.actual,
    this.effort,
    this.durationMin,
    this.notes,
    String? updatedAt,
  }) : updatedAt = updatedAt ?? nowUtcIso();

  bool get counts => status == 'done' || status == 'partial';

  factory SessionLog.fromJson(Map<String, dynamic> j) => SessionLog(
        status: j['status'] as String,
        actual: _d(j['actual']),
        effort: _i(j['effort']),
        durationMin: _d(j['duration_min']),
        notes: j['notes'] as String?,
        updatedAt: j['updated_at'] as String?,
      );

  Map<String, dynamic> toJson() => {
        'status': status,
        'actual': actual,
        'effort': effort,
        'duration_min': durationMin,
        'notes': notes,
        'updated_at': updatedAt,
      };
}

class Session {
  final int id;
  final String date;
  final int week;
  final String day;
  final String phase;
  final String timeSlot;
  final String type; // Run | Swim | Strength | Mobility | Rest
  final String title;
  final String details;
  final double planned;
  final String unit;
  SessionLog? log;

  Session({
    required this.id,
    required this.date,
    required this.week,
    required this.day,
    required this.phase,
    required this.timeSlot,
    required this.type,
    required this.title,
    required this.details,
    required this.planned,
    required this.unit,
    this.log,
  });

  DateTime get dateTime => DateTime.parse(date);
  bool get isTraining => type != 'Rest';
  bool get isFastDay => title.startsWith('FAST DAY') || day == 'Monday' || day == 'Thursday';

  /// Title without the "FAST DAY — " prefix, for compact cards.
  String get shortTitle => title.replaceFirst('FAST DAY — ', '');

  String get plannedLabel {
    if (planned == 0) return '';
    final value = planned == planned.roundToDouble() ? planned.toStringAsFixed(0) : planned.toStringAsFixed(1);
    switch (unit) {
      case 'km':
        return '$value km';
      case 'm':
        return '$value m';
      default:
        return '$value min';
    }
  }

  factory Session.fromJson(Map<String, dynamic> j) => Session(
        id: j['id'] as int,
        date: j['date'] as String,
        week: j['week'] as int,
        day: j['day'] as String,
        phase: j['phase'] as String,
        timeSlot: j['time_slot'] as String,
        type: j['type'] as String,
        title: j['title'] as String,
        details: j['details'] as String,
        planned: _d(j['planned']) ?? 0,
        unit: j['unit'] as String,
        log: j['log'] == null ? null : SessionLog.fromJson(Map<String, dynamic>.from(j['log'] as Map)),
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'date': date,
        'week': week,
        'day': day,
        'phase': phase,
        'time_slot': timeSlot,
        'type': type,
        'title': title,
        'details': details,
        'planned': planned,
        'unit': unit,
        'log': log?.toJson(),
      };
}

/// The 2-minute daily log (plan section 14) plus optional food and habit details.
class Habit {
  final String date;
  double? weight;
  int? restingHr;
  double? sleepHours;
  int? sleepQuality;
  int? soreness;
  int? pain;
  String? painWhere;
  int? energy;
  int? mood;
  int? motivation;
  int? nutrition;
  int? fastTolerance;
  bool? warningSigns;
  bool? fastKept;
  double? waterLitres;
  int? proteinG;
  int? calories;
  int? vegServings;
  bool? sunlight;
  bool? kegel1;
  bool? kegel2;
  String? notes;
  String updatedAt;

  Habit({
    required this.date,
    this.weight,
    this.restingHr,
    this.sleepHours,
    this.sleepQuality,
    this.soreness,
    this.pain,
    this.painWhere,
    this.energy,
    this.mood,
    this.motivation,
    this.nutrition,
    this.fastTolerance,
    this.warningSigns,
    this.fastKept,
    this.waterLitres,
    this.proteinG,
    this.calories,
    this.vegServings,
    this.sunlight,
    this.kegel1,
    this.kegel2,
    this.notes,
    String? updatedAt,
  }) : updatedAt = updatedAt ?? nowUtcIso();

  factory Habit.fromJson(Map<String, dynamic> j) => Habit(
        date: j['date'] as String,
        weight: _d(j['weight']),
        restingHr: _i(j['resting_hr']),
        sleepHours: _d(j['sleep_hours']),
        sleepQuality: _i(j['sleep_quality']),
        soreness: _i(j['soreness']),
        pain: _i(j['pain']),
        painWhere: j['pain_where'] as String?,
        energy: _i(j['energy']),
        mood: _i(j['mood']),
        motivation: _i(j['motivation']),
        nutrition: _i(j['nutrition']),
        fastTolerance: _i(j['fast_tolerance']),
        warningSigns: _b(j['warning_signs']),
        fastKept: _b(j['fast_kept']),
        waterLitres: _d(j['water_litres']),
        proteinG: _i(j['protein_g']),
        calories: _i(j['calories']),
        vegServings: _i(j['veg_servings']),
        sunlight: _b(j['sunlight']),
        kegel1: _b(j['kegel_1']),
        kegel2: _b(j['kegel_2']),
        notes: j['notes'] as String?,
        updatedAt: j['updated_at'] as String?,
      );

  /// Body for PUT /api/habits/{date}
  Map<String, dynamic> toBody() => {
        'weight': weight,
        'resting_hr': restingHr,
        'sleep_hours': sleepHours,
        'sleep_quality': sleepQuality,
        'soreness': soreness,
        'pain': pain,
        'pain_where': painWhere,
        'energy': energy,
        'mood': mood,
        'motivation': motivation,
        'nutrition': nutrition,
        'fast_tolerance': fastTolerance,
        'warning_signs': warningSigns,
        'fast_kept': fastKept,
        'water_litres': waterLitres,
        'protein_g': proteinG,
        'calories': calories,
        'veg_servings': vegServings,
        'sunlight': sunlight,
        'kegel_1': kegel1,
        'kegel_2': kegel2,
        'notes': notes,
        'updated_at': updatedAt,
      };

  Map<String, dynamic> toJson() => {'date': date, ...toBody()};
}

/// Weekly check-in: waist, longest continuous swim, 5 km test, notes. Weight comes from the daily log.
class Checkin {
  final int week;
  final String label;
  final String date;
  final double? targetWeight; // expected range, slow end (0.3 kg/week)
  final double? stretchWeight; // expected range, fast end (0.5 kg/week)
  final double? plannedLongRun; // minutes
  final double? plannedSwim; // metres continuous
  double? weight;
  double? waist;
  double? longRunActual; // minutes
  double? swimNonstopActual;
  double? tt5kMin;
  int? energy;
  String? notes;
  String? updatedAt;

  Checkin({
    required this.week,
    required this.label,
    required this.date,
    this.targetWeight,
    this.stretchWeight,
    this.plannedLongRun,
    this.plannedSwim,
    this.weight,
    this.waist,
    this.longRunActual,
    this.swimNonstopActual,
    this.tt5kMin,
    this.energy,
    this.notes,
    this.updatedAt,
  });

  bool get logged => waist != null || longRunActual != null || swimNonstopActual != null || tt5kMin != null;

  /// Weeks with a planned 5 km test.
  bool get testWeek => week == 4 || week == 8 || week == 11;

  factory Checkin.fromJson(Map<String, dynamic> j) => Checkin(
        week: j['week'] as int,
        label: j['label'] as String,
        date: j['date'] as String,
        targetWeight: _d(j['target_weight']),
        stretchWeight: _d(j['stretch_weight']),
        plannedLongRun: _d(j['planned_long_run']),
        plannedSwim: _d(j['planned_swim']),
        weight: _d(j['weight']),
        waist: _d(j['waist']),
        longRunActual: _d(j['long_run_actual']),
        swimNonstopActual: _d(j['swim_nonstop_actual']),
        tt5kMin: _d(j['tt_5k_min']),
        energy: _i(j['energy']),
        notes: j['notes'] as String?,
        updatedAt: j['updated_at'] as String?,
      );

  Map<String, dynamic> toBody() => {
        'weight': weight,
        'waist': waist,
        'long_run_actual': longRunActual,
        'swim_nonstop_actual': swimNonstopActual,
        'tt_5k_min': tt5kMin,
        'energy': energy,
        'notes': notes,
        'updated_at': updatedAt ?? nowUtcIso(),
      };

  Map<String, dynamic> toJson() => {
        'week': week,
        'label': label,
        'date': date,
        'target_weight': targetWeight,
        'stretch_weight': stretchWeight,
        'planned_long_run': plannedLongRun,
        'planned_swim': plannedSwim,
        ...toBody(),
      };
}

/// One queued change waiting to reach the server.
class PendingChange {
  final String method; // PUT | DELETE
  final String path;
  final Map<String, dynamic>? body;

  PendingChange(this.method, this.path, this.body);

  factory PendingChange.fromJson(Map<String, dynamic> j) => PendingChange(
        j['method'] as String,
        j['path'] as String,
        j['body'] == null ? null : Map<String, dynamic>.from(j['body'] as Map),
      );

  Map<String, dynamic> toJson() => {'method': method, 'path': path, 'body': body};
}

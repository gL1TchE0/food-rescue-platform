import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';

/// Local SQLite Database for Offline-First Operations
/// Stores tasks and locations when network unavailable

class LocalDatabase {
  static final LocalDatabase instance = LocalDatabase._init();
  static Database? _database;

  LocalDatabase._init();

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDB('m7_volunteer.db');
    return _database!;
  }

  Future<Database> _initDB(String filePath) async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, filePath);

    return await openDatabase(
      path,
      version: 1,
      onCreate: _createDB,
    );
  }

  Future _createDB(Database db, int version) async {
    const idType = 'TEXT PRIMARY KEY';
    const textType = 'TEXT NOT NULL';
    const intType = 'INTEGER NOT NULL';
    const realType = 'REAL NOT NULL';

    // Offline Tasks Table
    await db.execute('''
      CREATE TABLE offline_tasks (
        id $idType,
        donor_id $textType,
        ngo_id $textType,
        pickup_lat $realType,
        pickup_lng $realType,
        drop_lat $realType,
        drop_lng $realType,
        food_type TEXT,
        expiry_time $textType,
        status $textType,
        synced $intType DEFAULT 0
      )
    ''');

    // Location Queue (for offline GPS tracking)
    await db.execute('''
      CREATE TABLE location_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id $textType,
        lat $realType,
        lng $realType,
        speed $realType,
        heading $realType,
        timestamp $textType,
        synced $intType DEFAULT 0
      )
    ''');

    // Exception Queue
    await db.execute('''
      CREATE TABLE exception_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id $textType,
        issue_type $textType,
        description TEXT,
        timestamp $textType,
        synced $intType DEFAULT 0
      )
    ''');
  }

  /// Save location update to queue
  Future<int> insertLocationUpdate(Map<String, dynamic> location) async {
    final db = await instance.database;
    return await db.insert('location_queue', location);
  }

  /// Get unsynced locations
  Future<List<Map<String, dynamic>>> getUnsyncedLocations() async {
    final db = await instance.database;
    return await db.query(
      'location_queue',
      where: 'synced = ?',
      whereArgs: [0],
    );
  }

  /// Mark location as synced
  Future<int> markLocationSynced(int id) async {
    final db = await instance.database;
    return await db.update(
      'location_queue',
      {'synced': 1},
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  /// Save task offline
  Future<int> insertTask(Map<String, dynamic> task) async {
    final db = await instance.database;
    return await db.insert(
      'offline_tasks',
      task,
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  /// Get unsynced tasks
  Future<List<Map<String, dynamic>>> getUnsyncedTasks() async {
    final db = await instance.database;
    return await db.query(
      'offline_tasks',
      where: 'synced = ?',
      whereArgs: [0],
    );
  }

  /// Close database
  Future close() async {
    final db = await instance.database;
    db.close();
  }
}

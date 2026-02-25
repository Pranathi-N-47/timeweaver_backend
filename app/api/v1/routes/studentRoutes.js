const express = require('express');
const router = express.Router();
const db = require('../config/db');

// ============ STUDENT REGISTRATION ============

// Get student's registrations for a semester
router.get('/registrations/:student_id', async (req, res) => {
    const { student_id } = req.params;
    const { semester_id } = req.query;

    try {
        let query = `
            SELECT r.*, c.name as course_name, c.code as course_code, c.credits 
            FROM student_registrations r 
            JOIN courses c ON r.course_id = c.id 
            WHERE r.student_id = $1
        `;
        const params = [student_id];

        if (semester_id) {
            query += ' AND r.semester_id = $2';
            params.push(semester_id);
        }

        const result = await db.query(query, params);
        res.json(result.rows);
    } catch (err) {
        console.error('Error fetching registrations:', err);
        res.status(500).json({ error: 'Failed to fetch registrations' });
    }
});

// Register for a course
router.post('/register', async (req, res) => {
    const { student_id, course_id, semester_id } = req.body;

    if (!student_id || !course_id || !semester_id) {
        return res.status(400).json({ error: 'Missing student_id, course_id, or semester_id' });
    }

    try {
        // 1. Check if student has backlogs
        const backlogResult = await db.query(
            'SELECT COUNT(*) FROM student_results WHERE student_id = $1 AND is_backlog = TRUE',
            [student_id]
        );
        const hasBacklogs = parseInt(backlogResult.rows[0].count) > 0;
        const limit = hasBacklogs ? 8 : 6;

        // 2. Check current registration count
        const countResult = await db.query(
            'SELECT COUNT(*) FROM student_registrations WHERE student_id = $1 AND semester_id = $2 AND status = \'registered\'',
            [student_id, semester_id]
        );

        const count = parseInt(countResult.rows[0].count);
        if (count >= limit) {
            return res.status(400).json({
                error: `Registration limit reached. ${hasBacklogs ? 'As you have backlogs, your limit is 8.' : 'Your limit is 6.'} You can only register for up to ${limit} courses per semester.`
            });
        }

        // 3. Register for the course
        const result = await db.query(
            'INSERT INTO student_registrations (student_id, course_id, semester_id) VALUES ($1, $2, $3) RETURNING *',
            [student_id, course_id, semester_id]
        );

        res.status(201).json(result.rows[0]);
    } catch (err) {
        console.error('Error registering for course:', err);
        if (err.code === '23505') {
            return res.status(409).json({ error: 'Already registered for this course in this semester' });
        }
        res.status(500).json({ error: 'Failed to register for course' });
    }
});

// ============ STUDENT BACKLOGS ============

// Get student's backlogs
router.get('/backlogs/:student_id', async (req, res) => {
    const { student_id } = req.params;

    try {
        const result = await db.query(
            `SELECT sr.*, c.name as course_name, c.code as course_code 
             FROM student_results sr 
             JOIN courses c ON sr.course_id = c.id 
             WHERE sr.student_id = $1 AND sr.is_backlog = TRUE`,
            [student_id]
        );
        res.json(result.rows);
    } catch (err) {
        console.error('Error fetching backlogs:', err);
        res.status(500).json({ error: 'Failed to fetch backlogs' });
    }
});

module.exports = router;
